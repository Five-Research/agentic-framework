"""Pytest configuration file for agentic framework tests.

This file contains fixtures and configuration for pytest to run tests
for the agentic framework library.
"""

import os
import sys
import json
import pytest
from unittest.mock import MagicMock

# Add parent directory to path to import agentic_library
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def test_personality():
    """Fixture providing a test personality configuration."""
    return {
        "name": "Test Agent",
        "bio": "A test agent for unit testing",
        "interests": ["AI", "technology", "science"],
        "tone": "friendly",
        "emotional_state": {
            "base_state": "neutral",
            "current_state": "curious",
            "intensity": 0.6,
            "decay_rate": 0.1,
            "triggers": {
                "excited": ["amazing", "awesome", "great"],
                "concerned": ["problem", "issue", "worried"]
            }
        },
        "memory": {
            "short_term": {
                "capacity": 5,
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


@pytest.fixture
def mock_llm_provider():
    """Fixture providing a mock LLM provider."""
    mock_provider = MagicMock()
    mock_provider.generate_response.return_value = {
        "text": "This is a mock response from the LLM provider.",
        "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20}
    }
    return mock_provider


@pytest.fixture
def test_memory_dir(tmpdir):
    """Fixture providing a temporary directory for memory storage."""
    memory_dir = tmpdir.mkdir("test_memory")
    return str(memory_dir)


@pytest.fixture
def test_personality_file(tmpdir, test_personality):
    """Fixture providing a temporary personality file."""
    personality_file = tmpdir.join("test_personality.json")
    with open(personality_file, 'w') as f:
        json.dump(test_personality, f)
    return str(personality_file)