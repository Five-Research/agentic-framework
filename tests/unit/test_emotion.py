import unittest
import time
from unittest.mock import patch, MagicMock

from agentic_library.emotion import EmotionEngine, EmotionState


class TestEmotionEngine(unittest.TestCase):
    """Unit tests for the Emotion Engine component."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_personality = {
            "name": "Test Agent",
            "emotional_state": {
                "base_state": "neutral",
                "current_state": "curious",
                "intensity": 0.6,
                "decay_rate": 0.1,
                "triggers": {
                    "excited": ["amazing", "awesome", "great"],
                    "concerned": ["problem", "issue", "worried"]
                }
            }
        }
        self.emotion_engine = EmotionEngine(self.test_personality)
    
    def test_initialization(self):
        """Test that the emotion engine initializes correctly."""
        # Check that the current emotion is set from the personality
        self.assertEqual(self.emotion_engine.current_emotion.name, "curious")
        self.assertEqual(self.emotion_engine.current_emotion.intensity, 0.6)
        
        # Check that the base state is set correctly
        self.assertEqual(self.emotion_engine.base_state, "neutral")
        
        # Check that the decay rate is set correctly
        self.assertEqual(self.emotion_engine.decay_rate, 0.1)
        
        # Check that the triggers are set correctly
        self.assertIn("excited", self.emotion_engine.triggers)
        self.assertIn("concerned", self.emotion_engine.triggers)
        self.assertIn("amazing", self.emotion_engine.triggers["excited"])
        self.assertIn("problem", self.emotion_engine.triggers["concerned"])
    
    def test_default_initialization(self):
        """Test initialization with minimal personality configuration."""
        minimal_personality = {"name": "Minimal Agent"}
        emotion_engine = EmotionEngine(minimal_personality)
        
        # Check that default values are used
        self.assertEqual(emotion_engine.current_emotion.name, "neutral")
        self.assertEqual(emotion_engine.base_state, "neutral")
        self.assertEqual(emotion_engine.decay_rate, 0.1)
        self.assertEqual(emotion_engine.triggers, {})
    
    def test_update_emotion(self):
        """Test updating emotion based on content."""
        # Test triggering excited emotion
        self.emotion_engine.update_emotion("This is an amazing development!")
        self.assertEqual(self.emotion_engine.current_emotion.name, "excited")
        self.assertGreater(self.emotion_engine.current_emotion.intensity, 0.6)
        
        # Test triggering concerned emotion
        self.emotion_engine.update_emotion("We have a problem with the system.")
        self.assertEqual(self.emotion_engine.current_emotion.name, "concerned")
        
        # Test no trigger words
        original_state = self.emotion_engine.current_emotion.name
        original_intensity = self.emotion_engine.current_emotion.intensity
        self.emotion_engine.update_emotion("This is a neutral statement.")
        # Should remain the same or decay slightly
        self.assertEqual(self.emotion_engine.current_emotion.name, original_state)
        self.assertLessEqual(self.emotion_engine.current_emotion.intensity, original_intensity)
    
    def test_emotion_decay(self):
        """Test that emotions decay over time."""
        # Set a non-base emotion
        self.emotion_engine.current_emotion = EmotionState(
            name="excited",
            intensity=0.8,
            timestamp=time.time() - 3600  # 1 hour ago
        )
        
        # Update with neutral content to trigger decay
        self.emotion_engine.update_emotion("Just checking in.")
        
        # Emotion should have decayed toward base state
        self.assertLess(self.emotion_engine.current_emotion.intensity, 0.8)
        
        # With enough time, should return to base state
        self.emotion_engine.current_emotion = EmotionState(
            name="excited",
            intensity=0.8,
            timestamp=time.time() - 86400  # 24 hours ago
        )
        self.emotion_engine.update_emotion("Just checking in again.")
        self.assertEqual(self.emotion_engine.current_emotion.name, "neutral")
    
    def test_get_emotion_influence(self):
        """Test getting the influence of the current emotion on decision making."""
        # Set a specific emotion
        self.emotion_engine.current_emotion = EmotionState(
            name="excited",
            intensity=0.8,
            timestamp=time.time()
        )
        
        influence = self.emotion_engine.get_emotion_influence()
        
        # Check that the influence contains the expected keys
        self.assertIn("action_probability", influence)
        self.assertIn("engagement_threshold", influence)
        self.assertIn("content_style", influence)
        
        # Check that the values are scaled by intensity
        base_influence = self.emotion_engine.EMOTION_INFLUENCES["excited"]
        self.assertAlmostEqual(
            influence["action_probability"],
            base_influence["action_probability"] * 0.8,
            places=2
        )
    
    def test_get_current_emotion(self):
        """Test getting the current emotion state."""
        emotion_state = self.emotion_engine.get_current_emotion()
        
        # Check that it returns an EmotionState object
        self.assertIsInstance(emotion_state, EmotionState)
        
        # Check that the values match the current emotion
        self.assertEqual(emotion_state.name, self.emotion_engine.current_emotion.name)
        self.assertEqual(emotion_state.intensity, self.emotion_engine.current_emotion.intensity)


if __name__ == "__main__":
    unittest.main()