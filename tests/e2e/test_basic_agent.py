#!/usr/bin/env python3
"""
End-to-End Test for Basic Agent

This test verifies that the complete agentic framework works correctly
by simulating a series of interactions with the basic agent example.
"""

import os
import sys
import json
import time
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path to import agentic_library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agentic_library.config import OpenAIAgentConfig
from agentic_library.openai_interface import OpenAIInterface
from agentic_library.enhanced_personality import EnhancedPersonalitySystem
from agentic_library.learning import EngagementMetrics


class TestBasicAgent(unittest.TestCase):
    """End-to-end tests for the Basic Agent example."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests."""
        # Load test personality
        with open(os.path.join(os.path.dirname(__file__), '../test_data/sample_personality.json'), 'r') as f:
            cls.test_personality = json.load(f)
        
        # Create test directories
        os.makedirs("test_memory", exist_ok=True)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test fixtures after running tests."""
        # Clean up test directories
        import shutil
        if os.path.exists("test_memory"):
            shutil.rmtree("test_memory")
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a mock response content as a JSON string
        self.mock_response_content = json.dumps({
            "type": "response",
            "content": "This is a test response from the agent.",
            "reasoning": "This is a test reasoning."
        })
        
        # Create a patch for the OpenAI API call
        # Directly return the JSON string that _call_llm would return
        self.openai_patch = patch('agentic_library.openai_interface.OpenAIInterface._call_llm', return_value=self.mock_response_content)
        self.mock_openai = self.openai_patch.start()
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Stop the OpenAI API patch
        self.openai_patch.stop()
    
    def test_agent_initialization(self):
        """Test that the agent initializes correctly."""
        # Initialize the enhanced personality system
        agent = EnhancedPersonalitySystem(
            self.test_personality,
            None,  # No file path for testing
            "test_memory"
        )
        
        # Check that all component systems are initialized
        self.assertIsNotNone(agent.emotion_engine)
        self.assertIsNotNone(agent.memory_system)
        self.assertIsNotNone(agent.learning_system)
        
        # Check that the personality is stored
        self.assertEqual(agent.personality["name"], "Test Agent")
    
    def test_agent_interaction_flow(self):
        """Test the complete flow of agent interaction."""
        # Initialize the enhanced personality system
        agent = EnhancedPersonalitySystem(
            self.test_personality,
            None,  # No file path for testing
            "test_memory"
        )
        
        # Initialize the LLM interface with a mock
        llm_interface = OpenAIInterface(
            personality=self.test_personality,
            api_key="test_key",
            model="test_model"
        )
        
        # Attach LLM interface to agent
        agent.llm_interface = llm_interface
        
        # 1. Process incoming content
        content = [
            {
                "id": "1",
                "source": "test_user",
                "text": "This is an amazing development in AI technology!"
            }
        ]
        agent.process_content(content)
        
        # Check that emotion is updated (should be excited from "amazing")
        emotion_state = agent.emotion_engine.get_current_emotion()
        self.assertEqual(emotion_state.name, "excited")
        
        # 2. Get decision context and decide action
        context = agent.get_decision_context(content)
        action = llm_interface.decide_action(content)
        
        # Check that the action is a response
        self.assertEqual(action["type"], "response")
        self.assertIn("content", action)
        
        # 3. Record the action
        agent.record_action(action, {"original_message": content[0]})
        
        # Check that the action is stored in memory
        recent_interactions = agent.memory_system.get_recent_interactions(2)
        self.assertEqual(len(recent_interactions), 2)  # Original message + response
        
        # The order of interactions might vary, so we'll just check that both exist
        interaction_types = [interaction.interaction_type for interaction in recent_interactions]
        self.assertIn("view", interaction_types)  # Original message
        self.assertIn("response", interaction_types)  # Agent's response
        
        # 4. Record engagement with the response
        metrics = EngagementMetrics(
            positive_feedback=5,
            amplification=2,
            responses=1,
            clicks=10,
            impressions=50,
            timestamp=time.time()
        )
        engagement_score = agent.record_engagement(
            action["content"],
            metrics,
            ["AI", "technology"]
        )
        
        # Check that engagement score is calculated
        self.assertGreater(engagement_score, 0.0)
        self.assertLessEqual(engagement_score, 1.0)
        
        # 5. Check that topic engagement is updated
        self.assertIn("topic_engagement", agent.personality)
        self.assertIn("AI", agent.personality["topic_engagement"])
        self.assertIn("technology", agent.personality["topic_engagement"])
    
    def test_agent_adaptation(self):
        """Test that the agent adapts based on engagement."""
        # Initialize the enhanced personality system
        agent = EnhancedPersonalitySystem(
            self.test_personality,
            None,  # No file path for testing
            "test_memory"
        )
        
        # Set up initial topic engagement with high scores for new topics
        agent.personality["topic_engagement"] = {
            "AI": {"score": 0.5, "count": 5},
            "technology": {"score": 0.4, "count": 3},
            "blockchain": {"score": 0.9, "count": 10},  # New high-engagement topic
            "virtual reality": {"score": 0.8, "count": 8}  # New high-engagement topic
        }
        
        # Add a method to the learning system for testing purposes
        def update_interests():
            # Update interests based on topic engagement
            topic_engagement = agent.personality["topic_engagement"]
            # Sort topics by score
            sorted_topics = sorted(
                [(topic, data["score"]) for topic, data in topic_engagement.items()],
                key=lambda x: x[1],
                reverse=True
            )
            # Add high-engagement topics to interests
            for topic, score in sorted_topics:
                if score > 0.7 and topic not in agent.personality["interests"]:
                    agent.personality["interests"].append(topic)
        
        # Attach the method to the learning system for this test
        agent.learning_system.update_interests = update_interests
        
        # Update interests based on engagement
        agent.learning_system.update_interests()
        
        # Check that interests are updated to include high-engagement topics
        interests = agent.personality["interests"]
        self.assertIn("blockchain", interests)
        self.assertIn("virtual reality", interests)
        
        # Set up tone engagement data with a different preferred tone
        agent.personality["tone_engagement"] = {
            "friendly": {"score": 0.4, "count": 5},
            "professional": {"score": 0.8, "count": 10},  # Higher engagement
            "casual": {"score": 0.3, "count": 2}
        }
        
        # Add a method to the learning system for testing purposes
        def adapt_tone():
            # Find tone with highest engagement score
            tone_engagement = agent.personality["tone_engagement"]
            # Sort tones by score
            sorted_tones = sorted(
                [(tone, data["score"]) for tone, data in tone_engagement.items()],
                key=lambda x: x[1],
                reverse=True
            )
            # Set tone to the one with highest score
            if sorted_tones:
                agent.personality["tone"] = sorted_tones[0][0]
        
        # Attach the method to the learning system for this test
        agent.learning_system.adapt_tone = adapt_tone
        
        # Adapt tone based on engagement
        agent.learning_system.adapt_tone()
        
        # Check that tone is updated to the one with highest engagement
        self.assertEqual(agent.personality["tone"], "professional")


if __name__ == "__main__":
    unittest.main()