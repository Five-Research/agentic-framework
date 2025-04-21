#!/usr/bin/env python3
"""
Agent Demo Application

This demo application showcases the complete agentic framework with emotion,
memory, and learning capabilities integrated into a cohesive agent.

It provides an interactive way to test the agent's behavior and verify that
all components are working correctly together.

Usage:
    python agent_demo.py [--personality PERSONALITY_FILE]
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger

# Add parent directory to path to import agentic_library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import agentic library modules
from agentic_library.enhanced_personality import EnhancedPersonalitySystem
from agentic_library.openai_interface import OpenAIInterface
from agentic_library.learning import EngagementMetrics


def setup_logging(log_level):
    """Configure the logging system."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    logger.add(
        "logs/agent_demo_{time:YYYY-MM-DD}.log",
        rotation="500 MB",
        retention="10 days",
        level="DEBUG"
    )


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Agent Demo Application")
    parser.add_argument(
        "--personality", 
        type=str,
        default="default_personality.json",
        help="Path to personality configuration file"
    )
    return parser.parse_args()


def create_default_personality():
    """Create a default personality configuration if none is provided."""
    personality = {
        "name": "Demo Agent",
        "bio": "A demonstration agent for testing the agentic framework",
        "interests": ["AI", "technology", "science", "art", "music"],
        "tone": "friendly",
        "emotional_state": {
            "base_state": "neutral",
            "current_state": "curious",
            "intensity": 0.6,
            "decay_rate": 0.1,
            "triggers": {
                "excited": ["amazing", "awesome", "great", "excellent"],
                "curious": ["interesting", "wonder", "question", "how"],
                "thoughtful": ["consider", "think", "reflect", "ponder"],
                "amused": ["funny", "laugh", "joke", "humor"],
                "concerned": ["problem", "issue", "worried", "concern"]
            }
        },
        "memory": {
            "short_term": {
                "capacity": 10,
                "decay_rate": 0.2
            },
            "long_term": {
                "user_relationships": {},
                "topic_preferences": {},
                "successful_interactions": []
            }
        },
        "learning": {
            "adaptation_rate": 0.1,
            "interest_evolution": True,
            "engagement_learning": True,
            "metrics": {
                "positive_feedback_weight": 0.3,
                "amplification_weight": 0.5,
                "responses_weight": 0.2,
                "impressions_weight": 0.1
            }
        }
    }
    
    # Save the default personality
    with open("default_personality.json", 'w') as f:
        json.dump(personality, f, indent=2)
    
    return personality


def display_agent_state(agent):
    """Display the current state of the agent."""
    print("\n" + "=" * 50)
    print(f"AGENT STATE: {agent.personality['name']}")
    print("=" * 50)
    
    # Display emotional state
    emotion = agent.emotion_engine.get_current_emotion()
    print(f"Emotional State: {emotion['name']} (Intensity: {emotion['intensity']:.2f})")
    
    # Display recent interactions
    recent = agent.memory_system.get_recent_interactions(3)
    print("\nRecent Interactions:")
    for i, interaction in enumerate(recent):
        timestamp = datetime.fromtimestamp(interaction.timestamp).strftime('%H:%M:%S')
        print(f"  {i+1}. [{timestamp}] {interaction.user}: {interaction.content[:50]}...")
    
    # Display top interests
    interests = agent.personality.get("interests", [])
    print(f"\nInterests: {', '.join(interests[:5])}")
    
    # Display top user relationships
    relationships = agent.memory_system.user_relationships
    if relationships:
        print("\nTop Relationships:")
        sorted_users = sorted(relationships.items(), 
                             key=lambda x: x[1].get("familiarity", 0), 
                             reverse=True)[:3]
        for user, data in sorted_users:
            print(f"  {user}: Familiarity {data.get('familiarity', 0):.2f}, "
                  f"Sentiment {data.get('sentiment', 0):.2f}")
    
    print("=" * 50 + "\n")


def simulate_user_interaction(agent, user_id, message):
    """Simulate a user interaction with the agent."""
    print(f"\n[User {user_id}]: {message}")
    
    # Create content object
    content = [
        {
            "id": str(int(time.time())),
            "source": f"user{user_id}",
            "text": message
        }
    ]
    
    # Process the content
    agent.process_content(content)
    
    # Get decision context
    context = agent.get_decision_context(content)
    
    # Generate response using OpenAI interface
    action = agent.llm_interface.decide_action(content)
    
    # Record the action
    agent.record_action(action, {"original_message": content[0]})
    
    # Display the response
    if action["type"] == "response" or action["type"] == "message":
        print(f"\n[Agent]: {action.get('content', '')}")
    else:
        print(f"\n[Agent]: *{action['type']}*")
    
    return action


def simulate_engagement(agent, action, engagement_level="medium"):
    """Simulate engagement with the agent's response."""
    # Define engagement levels
    engagement_levels = {
        "low": {
            "positive_feedback": 1,
            "amplification": 0,
            "responses": 0,
            "clicks": 2,
            "impressions": 50
        },
        "medium": {
            "positive_feedback": 5,
            "amplification": 2,
            "responses": 1,
            "clicks": 10,
            "impressions": 50
        },
        "high": {
            "positive_feedback": 20,
            "amplification": 10,
            "responses": 5,
            "clicks": 30,
            "impressions": 100
        }
    }
    
    # Get engagement metrics for the specified level
    metrics_data = engagement_levels.get(engagement_level, engagement_levels["medium"])
    
    # Create engagement metrics
    metrics = EngagementMetrics(
        positive_feedback=metrics_data["positive_feedback"],
        amplification=metrics_data["amplification"],
        responses=metrics_data["responses"],
        clicks=metrics_data["clicks"],
        impressions=metrics_data["impressions"],
        timestamp=time.time()
    )
    
    # Extract topics from the action content
    content = action.get("content", "")
    
    # Simple topic extraction (in a real system, this would use NLP)
    topics = []
    for interest in agent.personality.get("interests", []):
        if interest.lower() in content.lower():
            topics.append(interest)
    
    # Record engagement
    engagement_score = agent.record_engagement(content, metrics, topics)
    
    print(f"\n[System]: Recorded engagement with score {engagement_score:.2f}")
    print(f"[System]: Topics detected: {', '.join(topics) if topics else 'None'}")
    
    return engagement_score


def interactive_mode(agent):
    """Run the agent in interactive mode."""
    print("\nWelcome to the Agent Demo Interactive Mode")
    print("Type 'exit' to quit, 'state' to see agent state, or any message to interact")
    
    user_id = input("\nEnter your user ID: ")
    
    while True:
        message = input(f"\n[User {user_id}]: ")
        
        if message.lower() == 'exit':
            break
        elif message.lower() == 'state':
            display_agent_state(agent)
            continue
        
        # Process the user message
        action = simulate_user_interaction(agent, user_id, message)
        
        # Ask about engagement
        engagement = input("\nRate engagement (low/medium/high): ").lower()
        if engagement in ["low", "medium", "high"]:
            simulate_engagement(agent, action, engagement)
        
        # Display updated state
        display_agent_state(agent)


def demo_mode(agent):
    """Run a predefined demo scenario."""
    print("\nRunning Demo Scenario")
    
    # Initial state
    print("\nInitial Agent State:")
    display_agent_state(agent)
    
    # Scenario 1: Excited response
    print("\n\nScenario 1: Excited Response")
    action1 = simulate_user_interaction(
        agent, "1", "I just saw an amazing breakthrough in AI technology!"
    )
    simulate_engagement(agent, action1, "high")
    display_agent_state(agent)
    
    # Scenario 2: Concerned response
    print("\n\nScenario 2: Concerned Response")
    action2 = simulate_user_interaction(
        agent, "2", "I'm worried about the ethical issues with these new AI systems."
    )
    simulate_engagement(agent, action2, "medium")
    display_agent_state(agent)
    
    # Scenario 3: Building relationship with user
    print("\n\nScenario 3: Building Relationship")
    for i in range(3):
        action3 = simulate_user_interaction(
            agent, "1", f"Let's discuss more about AI and art integration, round {i+1}."
        )
        simulate_engagement(agent, action3, "high")
    display_agent_state(agent)
    
    # Scenario 4: Learning new interests
    print("\n\nScenario 4: Learning New Interests")
    action4 = simulate_user_interaction(
        agent, "3", "Have you considered how blockchain technology could transform digital art ownership?"
    )
    simulate_engagement(agent, action4, "high")
    
    # Update interests based on engagement
    agent.learning_system.update_interests()
    display_agent_state(agent)
    
    print("\n\nDemo completed! The agent has demonstrated:")
    print("1. Emotional responses to different triggers")
    print("2. Memory of recent interactions")
    print("3. Relationship building with users")
    print("4. Learning and adapting interests based on engagement")


def main():
    """Main entry point for the Agent Demo application."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    setup_logging(log_level)
    
    logger.info("Starting Agent Demo Application")
    
    try:
        # Create directories if they don't exist
        os.makedirs("logs", exist_ok=True)
        os.makedirs("memory", exist_ok=True)
        
        # Load or create personality
        if os.path.exists(args.personality):
            with open(args.personality, 'r') as f:
                personality = json.load(f)
            logger.info(f"Loaded personality from {args.personality}")
        else:
            personality = create_default_personality()
            logger.info("Created default personality")
        
        # Initialize the enhanced personality system
        agent = EnhancedPersonalitySystem(
            personality,
            args.personality,
            "memory"
        )
        
        # Initialize the LLM interface
        openai_api_key = os.getenv("OPENROUTER_API_KEY")
        openai_model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1:free")
        
        if not openai_api_key:
            logger.error("OpenRouter API key not found in environment variables")
            print("Error: OpenRouter API key not found. Please set OPENROUTER_API_KEY in .env file.")
            return
        
        llm_interface = OpenAIInterface(
            personality=personality,
            api_key=openai_api_key,
            model=openai_model,
            personality_file_path=args.personality
        )
        
        # Attach LLM interface to agent
        agent.llm_interface = llm_interface
        
        # Ask user which mode to run
        mode = input("\nSelect mode (interactive/demo): ").lower()
        
        if mode == "interactive":
            interactive_mode(agent)
        else:
            demo_mode(agent)
        
        logger.info("Agent Demo completed successfully")
        
    except Exception as e:
        logger.error(f"Error in Agent Demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()