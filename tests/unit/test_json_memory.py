import unittest
import os
import json
import shutil
import time
from unittest.mock import patch, MagicMock

from agentic_library.json_memory import MemorySystem, Interaction


class TestJsonMemorySystem(unittest.TestCase):
    """Unit tests for the JSON Memory System component."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a test memory directory
        self.test_memory_dir = "test_memory"
        os.makedirs(self.test_memory_dir, exist_ok=True)
        
        self.test_personality = {
            "name": "Test Agent",
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
            }
        }
        self.memory_system = MemorySystem(self.test_personality, self.test_memory_dir)
    
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Remove the test memory directory
        if os.path.exists(self.test_memory_dir):
            shutil.rmtree(self.test_memory_dir)
    
    def test_initialization(self):
        """Test that the memory system initializes correctly."""
        # Check that the short-term memory is initialized
        self.assertEqual(len(self.memory_system.short_term_memory), 0)
        self.assertEqual(self.memory_system.short_term_capacity, 5)
        self.assertEqual(self.memory_system.short_term_decay_rate, 0.2)
        
        # Check that the directory structure is created
        self.assertTrue(os.path.exists(self.test_memory_dir))
        self.assertTrue(os.path.exists(os.path.join(self.test_memory_dir, "interactions")))
        self.assertTrue(os.path.exists(os.path.join(self.test_memory_dir, "relationships")))
        self.assertTrue(os.path.exists(os.path.join(self.test_memory_dir, "topics")))
    
    def test_default_initialization(self):
        """Test initialization with minimal personality configuration."""
        minimal_personality = {"name": "Minimal Agent"}
        memory_system = MemorySystem(minimal_personality, self.test_memory_dir)
        
        # Check that default values are used
        self.assertEqual(memory_system.short_term_capacity, 20)  # Default capacity
        self.assertEqual(memory_system.short_term_decay_rate, 0.2)  # Default decay rate
    
    def test_store_interaction(self):
        """Test storing an interaction in memory."""
        # Create a test interaction
        interaction = Interaction(
            interaction_id="test_1",
            interaction_type="message",
            user="test_user",
            content="Hello, world!",
            timestamp=time.time()
        )
        
        # Store the interaction
        self.memory_system.store_interaction(interaction)
        
        # Check that it's in short-term memory
        self.assertEqual(len(self.memory_system.short_term_memory), 1)
        self.assertEqual(self.memory_system.short_term_memory[0].interaction_id, "test_1")
        
        # Check that it's saved to disk
        interactions_dir = os.path.join(self.test_memory_dir, "interactions")
        self.assertTrue(os.path.exists(interactions_dir))
        self.assertEqual(len(os.listdir(interactions_dir)), 1)
    
    def test_short_term_memory_capacity(self):
        """Test that short-term memory respects capacity limits."""
        # Add more interactions than the capacity
        for i in range(10):  # Capacity is 5
            interaction = Interaction(
                interaction_id=f"test_{i}",
                interaction_type="message",
                user="test_user",
                content=f"Message {i}",
                timestamp=time.time()
            )
            self.memory_system.store_interaction(interaction)
        
        # Check that only the most recent are kept
        self.assertEqual(len(self.memory_system.short_term_memory), 5)
        self.assertEqual(self.memory_system.short_term_memory[0].interaction_id, "test_5")
        self.assertEqual(self.memory_system.short_term_memory[-1].interaction_id, "test_9")
    
    def test_get_recent_interactions(self):
        """Test retrieving recent interactions."""
        # Add some interactions
        for i in range(5):
            interaction = Interaction(
                interaction_id=f"test_{i}",
                interaction_type="message",
                user="test_user",
                content=f"Message {i}",
                timestamp=time.time() - (5 - i)  # Older to newer
            )
            self.memory_system.store_interaction(interaction)
        
        # Get recent interactions
        recent = self.memory_system.get_recent_interactions(3)
        
        # Check that we get the most recent ones
        self.assertEqual(len(recent), 3)
        self.assertEqual(recent[0].interaction_id, "test_2")
        self.assertEqual(recent[-1].interaction_id, "test_4")
    
    def test_get_interactions_by_user(self):
        """Test retrieving interactions by user."""
        # Add interactions from different users
        users = ["alice", "bob", "alice", "charlie", "alice"]
        for i, user in enumerate(users):
            interaction = Interaction(
                interaction_id=f"test_{i}",
                interaction_type="message",
                user=user,
                content=f"Message from {user}",
                timestamp=time.time()
            )
            self.memory_system.store_interaction(interaction)
        
        # Get interactions by user
        alice_interactions = self.memory_system.get_interactions_by_user("alice")
        
        # Check that we get only Alice's interactions
        self.assertEqual(len(alice_interactions), 3)
        for interaction in alice_interactions:
            self.assertEqual(interaction.user, "alice")
    
    def test_update_user_relationship(self):
        """Test updating user relationship data."""
        # Update relationship with a user
        self.memory_system.update_user_relationship(
            username="test_user",
            familiarity=0.5,
            sentiment=0.7
        )
        
        # Check that the relationship is stored
        self.assertIn("test_user", self.memory_system.user_relationships)
        self.assertEqual(self.memory_system.user_relationships["test_user"]["familiarity"], 0.5)
        self.assertEqual(self.memory_system.user_relationships["test_user"]["sentiment"], 0.7)
        
        # Check that it's saved to disk
        relationships_file = os.path.join(self.test_memory_dir, "relationships.json")
        self.assertTrue(os.path.exists(relationships_file))
        
        # Update the same user again
        self.memory_system.update_user_relationship(
            username="test_user",
            familiarity=0.6,  # Increased
            sentiment=0.8     # Increased
        )
        
        # Check that the values are updated
        self.assertEqual(self.memory_system.user_relationships["test_user"]["familiarity"], 0.6)
        self.assertEqual(self.memory_system.user_relationships["test_user"]["sentiment"], 0.8)
    
    def test_get_user_relationship(self):
        """Test retrieving user relationship data."""
        # Add a relationship
        self.memory_system.update_user_relationship(
            username="test_user",
            familiarity=0.5,
            sentiment=0.7
        )
        
        # Get the relationship
        relationship = self.memory_system.get_user_relationship("test_user")
        
        # Check that we get the correct data
        self.assertIsInstance(relationship, dict)
        self.assertEqual(relationship["familiarity"], 0.5)
        self.assertEqual(relationship["sentiment"], 0.7)
        
        # Test getting a non-existent relationship
        unknown_relationship = self.memory_system.get_user_relationship("unknown_user")
        self.assertIsInstance(unknown_relationship, dict)
        self.assertEqual(unknown_relationship["familiarity"], 0.0)  # Default value
    
    def test_update_topic_preference(self):
        """Test updating topic preference data."""
        # Update preference for a topic
        self.memory_system.update_topic_preference(
            topic="AI",
            interest_level=0.8,
            engagement_score=0.6
        )
        
        # Check that the preference is stored
        self.assertIn("AI", self.memory_system.topic_preferences)
        self.assertEqual(self.memory_system.topic_preferences["AI"]["interest_level"], 0.8)
        self.assertEqual(self.memory_system.topic_preferences["AI"]["engagement_score"], 0.6)
        
        # Check that it's saved to disk
        topics_file = os.path.join(self.test_memory_dir, "topics.json")
        self.assertTrue(os.path.exists(topics_file))


if __name__ == "__main__":
    unittest.main()