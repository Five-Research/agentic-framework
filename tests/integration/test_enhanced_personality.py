import unittest
import os
import json
import shutil
import time
from unittest.mock import patch, MagicMock

from agentic_library.enhanced_personality import EnhancedPersonalitySystem
from agentic_library.json_memory import Interaction
from agentic_library.learning import EngagementMetrics


class TestEnhancedPersonalitySystem(unittest.TestCase):
    """Integration tests for the Enhanced Personality System."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create test directories
        self.test_memory_dir = "test_memory"
        os.makedirs(self.test_memory_dir, exist_ok=True)
        
        # Create a test personality file
        self.test_personality_file = "test_personality.json"
        self.test_personality = {
            "name": "Test Agent",
            "bio": "A test agent for integration testing",
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
        
        # Write the test personality to file
        with open(self.test_personality_file, 'w') as f:
            json.dump(self.test_personality, f)
        
        self.personality_system = EnhancedPersonalitySystem(
            self.test_personality,
            self.test_personality_file,
            self.test_memory_dir
        )
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Remove test files and directories
        if os.path.exists(self.test_personality_file):
            os.remove(self.test_personality_file)
        if os.path.exists(self.test_memory_dir):
            shutil.rmtree(self.test_memory_dir)
    
    def test_initialization(self):
        """Test that the enhanced personality system initializes correctly."""
        # Check that all component systems are initialized
        self.assertIsNotNone(self.personality_system.emotion_engine)
        self.assertIsNotNone(self.personality_system.memory_system)
        self.assertIsNotNone(self.personality_system.learning_system)
        
        # Check that the personality is stored
        self.assertEqual(self.personality_system.personality["name"], "Test Agent")
    
    def test_process_content(self):
        """Test processing content updates emotion and memory."""
        # Create test content
        content = [
            {
                "id": "1",
                "source": "user1",
                "text": "This is an amazing development in AI technology!"
            },
            {
                "id": "2",
                "source": "user2",
                "text": "We have a problem with the system that needs attention."
            }
        ]
        
        # Process the content
        self.personality_system.process_content(content)
        
        # Check that emotion is updated (should be excited from "amazing")
        emotion_state = self.personality_system.emotion_engine.get_current_emotion()
        self.assertEqual(emotion_state.name, "excited")
        
        # Check that interactions are stored in memory
        recent_interactions = self.personality_system.memory_system.get_recent_interactions(2)
        self.assertEqual(len(recent_interactions), 2)
        # Note: get_recent_interactions returns oldest first
        self.assertEqual(recent_interactions[0].user, "user1")
        self.assertEqual(recent_interactions[1].user, "user2")
    
    def test_record_action(self):
        """Test recording agent actions in memory."""
        # Create a test action
        action = {
            "type": "message",
            "content": "Hello, this is a test message.",
            "target": "user1"
        }
        
        # Record the action
        self.personality_system.record_action(action)
        
        # Check that the action is stored in memory
        recent_interactions = self.personality_system.memory_system.get_recent_interactions(1)
        self.assertEqual(len(recent_interactions), 1)
        self.assertEqual(recent_interactions[0].interaction_type, "message")
        self.assertEqual(recent_interactions[0].content, "Hello, this is a test message.")
        
        # Test recording a response action
        response_action = {
            "type": "response",
            "content": "This is a response to your question.",
            "target": "user2"
        }
        result = {
            "original_message": {
                "source": "user2",
                "text": "What do you think about this?"
            }
        }
        
        self.personality_system.record_action(response_action, result)
        
        # Check that the response is stored in memory
        recent_interactions = self.personality_system.memory_system.get_recent_interactions(2)
        self.assertEqual(len(recent_interactions), 2)
        # The implementation uses the action_type as the interaction_type
        self.assertEqual(recent_interactions[1].interaction_type, "response")
        self.assertEqual(recent_interactions[1].user, "user2")
    
    def test_record_engagement(self):
        """Test recording engagement metrics updates learning."""
        # Create test engagement metrics
        metrics = EngagementMetrics(
            positive_feedback=10,
            amplification=5,
            responses=3,
            clicks=20,
            impressions=100,
            timestamp=time.time()
        )
        
        # Record engagement for content with topics
        content = "This is a test post about AI and machine learning."
        topics = ["AI", "machine learning"]
        
        engagement_score = self.personality_system.record_engagement(content, metrics, topics)
        
        # Check that the engagement score is calculated correctly
        self.assertGreater(engagement_score, 0.0)
        self.assertLessEqual(engagement_score, 1.0)
        
        # Check that the topics are updated in the learning system's topic performance
        self.assertIn("AI", self.personality_system.learning_system.topic_performance)
        self.assertIn("machine learning", self.personality_system.personality.get("topic_engagement", {}))
        
        # Check that the personality file is updated
        with open(self.test_personality_file, 'r') as f:
            updated_personality = json.load(f)
        self.assertIn("topic_engagement", updated_personality)
    
    def test_get_decision_context(self):
        """Test getting decision context for LLM."""
        # Create test content
        content = [
            {
                "id": "1",
                "source": "user1",
                "text": "This is an amazing development in AI technology!"
            }
        ]
        
        # Process the content to update state
        self.personality_system.process_content(content)
        
        # Get decision context
        context = self.personality_system.get_decision_context(content)
        
        # Check that the context contains all required sections
        self.assertIn("personality", context)
        self.assertIn("emotional_state", context)
        self.assertIn("memory", context)
        self.assertIn("learning", context)
        
        # Check that the emotional state is correct
        self.assertEqual(context["emotional_state"]["current_emotion"], "excited")
        
        # Check that the memory contains the recent interaction
        self.assertEqual(len(context["memory"]["recent_interactions"]), 1)
        self.assertEqual(context["memory"]["recent_interactions"][0]["user"], "user1")
    
    def test_end_to_end_flow(self):
        """Test the complete flow of processing content, taking action, and recording engagement."""
        # 1. Process incoming content
        content = [
            {
                "id": "1",
                "source": "user1",
                "text": "This is an amazing development in AI technology!"
            }
        ]
        self.personality_system.process_content(content)
        
        # 2. Record an action taken by the agent
        action = {
            "type": "response",
            "content": "I'm excited about this development too! What aspects interest you most?",
            "target": "user1"
        }
        result = {
            "original_message": {
                "source": "user1",
                "text": "This is an amazing development in AI technology!"
            }
        }
        self.personality_system.record_action(action, result)
        
        # 3. Record engagement with the response
        metrics = EngagementMetrics(
            positive_feedback=5,
            amplification=2,
            responses=1,
            clicks=10,
            impressions=50,
            timestamp=time.time()
        )
        engagement_score = self.personality_system.record_engagement(
            action["content"],
            metrics,
            ["AI", "technology"]
        )
        
        # 4. Get decision context for next action
        context = self.personality_system.get_decision_context([])
        
        # Check that the flow has updated all systems correctly
        # Emotion should be excited
        self.assertEqual(context["emotional_state"]["current_emotion"], "excited")
        
        # Memory should have both interactions
        self.assertEqual(len(context["memory"]["recent_interactions"]), 2)
        
        # Learning should have updated topic engagement
        self.assertIn("AI", self.personality_system.personality.get("topic_engagement", {}))
        
        # Check that the personality file has been updated
        with open(self.test_personality_file, 'r') as f:
            updated_personality = json.load(f)
        self.assertIn("topic_engagement", updated_personality)


if __name__ == "__main__":
    unittest.main()