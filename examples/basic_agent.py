#!/usr/bin/env python3
"""
Basic Agent Example

This example demonstrates how to use the agentic library to create a simple
LLM-based agent with emotion, memory, and learning capabilities.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from loguru import logger

# Import agentic library modules
from agentic_library.config import OpenAIAgentConfig
from agentic_library.openai_interface import OpenAIInterface
from agentic_library.personality_validator import PersonalityValidator


def setup_logging(log_level):
    """Configure the logging system."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    logger.add(
        "logs/agent_{time:YYYY-MM-DD}.log",
        rotation="500 MB",
        retention="10 days",
        level="DEBUG"
    )


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Basic Agent Example")
    parser.add_argument(
        "--personality", 
        type=str,
        help="Path to personality configuration file"
    )
    return parser.parse_args()


def main():
    """Main entry point for the Basic Agent example."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    setup_logging(log_level)
    
    logger.info("Starting Basic Agent Example")
    
    try:
        # Create agent configuration
        config = OpenAIAgentConfig(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            personality_file=args.personality,
            memory_dir="agent_memory"
        )
        
        # Initialize the LLM interface with the agent's personality
        llm_interface = OpenAIInterface(
            personality=config.personality,
            api_key=config.api_key,
            model=config.model,
            personality_file_path=args.personality
        )
        
        # Example content to process
        sample_content = [
            {
                "id": "1",
                "source": "user1",
                "text": "I've been thinking about the ethical implications of AI in healthcare."
            },
            {
                "id": "2",
                "source": "user2",
                "text": "Has anyone experimented with using generative models for creating art?"
            }
        ]
        
        # Decide on an action based on the content
        action = llm_interface.decide_action(sample_content)
        
        # Display the action
        logger.info(f"Agent decided to take action: {action['type']}")
        if action['type'] in ['message', 'response']:
            logger.info(f"Content: {action.get('content', '')}")
        
        # Save the agent's state
        llm_interface.save_state()
        
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
    except Exception as e:
        logger.exception(f"Error running agent: {e}")
    finally:
        logger.info("Basic Agent Example stopped")


if __name__ == "__main__":
    main()