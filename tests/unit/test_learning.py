import unittest
import os
import json
import time
from unittest.mock import patch, MagicMock

from agentic_library.learning import LearningSystem, EngagementMetrics


class TestLearningSystem(unittest.TestCase):
    """Unit tests for the Learning System component."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a test personality file
        self.test_personality_file = "test_personality.json"
        self.test_personality = {
            "name": "Test Agent",
            "interests": ["AI", "technology", "science"],
            "tone": "friendly",
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
        
        self.learning_system = LearningSystem(self.test_personality, self.test_personality_file)
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Remove the test personality file
        if os.path.exists(self.test_personality_file):
            os.remove(self.test_personality_file)
    
    def test_initialization(self):
        """Test that the learning system initializes correctly."""
        # Check that the personality is stored
        self.assertEqual(self.learning_system.personality["name"], "Test Agent")
        
        # Check that the adaptation rate is set correctly
        self.assertEqual(self.learning_system.adaptation_rate, 0.1)
        
        # Check that the feature flags are set correctly
        self.assertTrue(self.learning_system.interest_evolution)
        self.assertTrue(self.learning_system.engagement_learning)
        
        # Check that the metric weights are set correctly
        self.assertEqual(self.learning_system.metric_weights["positive_feedback"], 0.3)
        self.assertEqual(self.learning_system.metric_weights["amplification"], 0.5)
    
    def test_default_initialization(self):
        """Test initialization with minimal personality configuration."""
        minimal_personality = {"name": "Minimal Agent"}
        learning_system = LearningSystem(minimal_personality)
        
        # Check that default values are used
        self.assertEqual(learning_system.adaptation_rate, 0.05)  # Default rate
        self.assertTrue(learning_system.interest_evolution)  # Default is True
        self.assertTrue(learning_system.engagement_learning)  # Default is True
    
    def test_record_engagement(self):
        """Test recording engagement metrics for content."""
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
        topics = ["AI", "machine learning"]
        engagement_score = self.learning_system.record_engagement(
            content="This is a test post about AI and machine learning.",
            metrics=metrics,
            topics=topics
        )
        
        # Check that the engagement score is calculated correctly
        self.assertGreater(engagement_score, 0.0)
        self.assertLessEqual(engagement_score, 1.0)
        
        # Check that the topics are updated in the topic performance tracking
        self.assertIn("AI", self.learning_system.topic_performance)
        self.assertIn("machine learning", self.learning_system.topic_performance)
    
    def test_update_interests(self):
        """Test updating interests based on engagement."""
        # Set up initial interests with engagement scores in topic_performance
        self.learning_system.topic_performance = {
            "AI": {"total_score": 3.5, "count": 5, "average": 0.7},
            "technology": {"total_score": 1.5, "count": 3, "average": 0.5},
            "science": {"total_score": 0.6, "count": 2, "average": 0.3},
            "art": {"total_score": 3.2, "count": 4, "average": 0.8}  # New high-engagement topic
        }
        
        # Update interests
        self.learning_system.update_interests()
        
        # Check that interests are updated based on engagement
        interests = self.learning_system.personality["interests"]
        self.assertIn("AI", interests)  # High engagement, should remain
        self.assertIn("art", interests)  # High engagement, should be added
        
        # Check that the personality file is updated
        with open(self.test_personality_file, 'r') as f:
            updated_personality = json.load(f)
        self.assertIn("art", updated_personality["interests"])
    
    def test_adapt_tone(self):
        """Test adapting tone based on engagement."""
        # Set up initial tone
        self.learning_system.personality["tone"] = "friendly"
        
        # Set up tone engagement data
        self.learning_system.personality["tone_engagement"] = {
            "friendly": {"score": 0.4, "count": 5},
            "professional": {"score": 0.7, "count": 3},  # Higher engagement
            "casual": {"score": 0.3, "count": 2}
        }
        
        # Adapt tone
        self.learning_system.adapt_tone()
        
        # Check that tone is updated to the one with highest engagement
        self.assertEqual(self.learning_system.personality["tone"], "professional")
        
        # Check that the personality file is updated
        with open(self.test_personality_file, 'r') as f:
            updated_personality = json.load(f)
        self.assertEqual(updated_personality["tone"], "professional")
    
    def test_save_personality(self):
        """Test saving personality changes to file."""
        # Make a change to the personality
        self.learning_system.personality["interests"].append("new interest")
        
        # Save the personality
        self.learning_system.save_personality()
        
        # Check that the file is updated
        with open(self.test_personality_file, 'r') as f:
            updated_personality = json.load(f)
        self.assertIn("new interest", updated_personality["interests"])
    
    def test_engagement_metrics(self):
        """Test the EngagementMetrics class."""
        # Create engagement metrics
        metrics = EngagementMetrics(
            positive_feedback=10,
            amplification=5,
            responses=3,
            clicks=20,
            impressions=100
        )
        
        # Test calculating engagement score with weights
        weights = {
            "positive_feedback": 0.3,
            "amplification": 0.5,
            "responses": 0.2,
            "impressions": 0.1
        }
        score = metrics.get_engagement_score(weights)
        
        # Check that the score is calculated correctly
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        # Test with empty weights
        empty_score = metrics.get_engagement_score({})
        self.assertEqual(empty_score, 0.0)


if __name__ == "__main__":
    unittest.main()