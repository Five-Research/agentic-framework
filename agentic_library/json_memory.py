"""JSON-based Memory System Module

This module provides memory capabilities for any LLM-based agent using JSON files,
allowing it to store and recall past interactions and develop relationships with users.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from loguru import logger


@dataclass
class Interaction:
    """Represents a single interaction with a user or content."""
    interaction_id: str
    interaction_type: str  # action type (e.g., message, response, query)
    user: str  # Identifier of the other party
    content: str  # Content of the interaction
    timestamp: float
    sentiment: float = 0.0  # -1.0 to 1.0
    engagement_score: float = 0.0  # 0.0 to 1.0


class MemorySystem:
    """Memory system for LLM-based agents using JSON files.
    
    This class handles storing and retrieving memories of past interactions,
    building relationships with users, and tracking topic preferences over time.
    """
    
    # Default memory configuration if none specified in personality
    DEFAULT_MEMORY_CONFIG = {
        "short_term": {
            "capacity": 20,
            "decay_rate": 0.2
        },
        "long_term": {
            "user_relationships": {},
            "topic_preferences": {},
            "successful_interactions": []
        }
    }
    
    def __init__(self, personality: Dict[str, Any], memory_dir: str = "memory"):
        """Initialize the memory system with a personality configuration.
        
        Args:
            personality: Dictionary containing personality configuration
            memory_dir: Directory path for storing JSON memory files
        """
        # Extract memory configuration from personality or use defaults
        self.memory_config = personality.get("memory", self.DEFAULT_MEMORY_CONFIG)
        
        # Initialize short-term memory (recent interactions)
        self.short_term_memory: List[Interaction] = []
        self.short_term_capacity = self.memory_config["short_term"]["capacity"]
        self.short_term_decay_rate = self.memory_config["short_term"]["decay_rate"]
        
        # Initialize long-term memory structures
        self.user_relationships = self.memory_config["long_term"]["user_relationships"]
        self.topic_preferences = self.memory_config["long_term"]["topic_preferences"]
        
        # Set up memory directory for persistent storage
        self.memory_dir = memory_dir
        self._initialize_memory_storage()
        
        # Load existing memory data if available
        self._load_memory_data()
        
        logger.info(f"Initialized JSON memory system with capacity: {self.short_term_capacity}")
    
    def _initialize_memory_storage(self) -> None:
        """Initialize the directory structure for JSON memory storage."""
        try:
            # Create memory directory if it doesn't exist
            os.makedirs(self.memory_dir, exist_ok=True)
            
            # Create subdirectories for different types of memory data
            os.makedirs(os.path.join(self.memory_dir, "interactions"), exist_ok=True)
            os.makedirs(os.path.join(self.memory_dir, "relationships"), exist_ok=True)
            os.makedirs(os.path.join(self.memory_dir, "topics"), exist_ok=True)
            
            logger.debug(f"Memory directory initialized at {self.memory_dir}")
            
        except Exception as e:
            logger.error(f"Error initializing memory directory: {e}")
    
    def _load_memory_data(self) -> None:
        """Load existing memory data from JSON files."""
        try:
            # Load user relationships
            relationships_file = os.path.join(self.memory_dir, "relationships.json")
            if os.path.exists(relationships_file):
                with open(relationships_file, 'r') as f:
                    self.user_relationships = json.load(f)
            
            # Load topic preferences
            topics_file = os.path.join(self.memory_dir, "topics.json")
            if os.path.exists(topics_file):
                with open(topics_file, 'r') as f:
                    self.topic_preferences = json.load(f)
            
            # Load recent interactions for short-term memory
            interactions_file = os.path.join(self.memory_dir, "recent_interactions.json")
            if os.path.exists(interactions_file):
                with open(interactions_file, 'r') as f:
                    interactions_data = json.load(f)
                    # Convert dictionary data back to Interaction objects
                    self.short_term_memory = [
                        Interaction(
                            interaction_id=item["interaction_id"],
                            interaction_type=item["interaction_type"],
                            user=item["user"],
                            content=item["content"],
                            timestamp=item["timestamp"],
                            sentiment=item["sentiment"],
                            engagement_score=item["engagement_score"]
                        ) for item in interactions_data
                    ]
            
            logger.debug("Memory data loaded from JSON files")
            
        except Exception as e:
            logger.error(f"Error loading memory data: {e}")
    
    def store_interaction(self, interaction: Interaction) -> None:
        """Store an interaction in memory.
        
        Args:
            interaction: Interaction object to store
        """
        # Add to short-term memory
        self.short_term_memory.append(interaction)
        
        # Trim short-term memory if it exceeds capacity
        if len(self.short_term_memory) > self.short_term_capacity:
            # Remove oldest interactions
            self.short_term_memory = sorted(
                self.short_term_memory,
                key=lambda x: x.timestamp,
                reverse=False
            )[-(self.short_term_capacity):]
        
        # Update user relationship
        self._update_user_relationship(interaction)
        
        # Update topic preferences based on content
        self._update_topic_preferences(interaction)
        
        # Store in JSON files for long-term persistence
        self._store_in_json_files(interaction)
        
        logger.debug(f"Stored interaction: {interaction.interaction_type} with {interaction.user}")
    
    def _update_user_relationship(self, interaction: Interaction) -> None:
        """Update relationship with a user based on interaction.
        
        Args:
            interaction: Interaction object
        """
        username = interaction.user
        
        # Skip self-interactions
        if username == "self":
            return
        
        # Initialize relationship if not exists
        if username not in self.user_relationships:
            self.user_relationships[username] = {
                "familiarity": 0.1,  # Initial familiarity
                "sentiment": 0.0,  # Neutral sentiment
                "last_interaction": interaction.timestamp,
                "interaction_count": 0
            }
        
        # Update existing relationship
        relationship = self.user_relationships[username]
        
        # Increase familiarity (with diminishing returns)
        familiarity_increase = 0.1 / (1 + relationship["interaction_count"] * 0.1)
        relationship["familiarity"] = min(1.0, relationship["familiarity"] + familiarity_increase)
        
        # Update sentiment based on interaction sentiment
        if interaction.sentiment != 0.0:
            # Weighted average of existing and new sentiment
            relationship["sentiment"] = (
                relationship["sentiment"] * 0.8 + interaction.sentiment * 0.2
            )
        
        # Update metadata
        relationship["last_interaction"] = interaction.timestamp
        relationship["interaction_count"] += 1
    
    def _update_topic_preferences(self, interaction: Interaction) -> None:
        """Update topic preferences based on interaction content.
        
        Args:
            interaction: Interaction object
        """
        # Extract potential topics from content
        content = interaction.content.lower()
        
        # Check for topics in content
        for topic in self._extract_topics(content):
            # Initialize topic if not exists
            if topic not in self.topic_preferences:
                self.topic_preferences[topic] = {
                    "interest_level": 0.5,  # Initial interest level
                    "engagement_rate": 0.0,
                    "last_interaction": interaction.timestamp,
                    "interaction_count": 0
                }
            
            # Update existing topic preference
            topic_pref = self.topic_preferences[topic]
            
            # Update engagement rate if available
            if interaction.engagement_score > 0.0:
                # Weighted average of existing and new engagement
                topic_pref["engagement_rate"] = (
                    topic_pref["engagement_rate"] * 0.8 + interaction.engagement_score * 0.2
                )
                
                # Adjust interest level based on engagement
                interest_change = (interaction.engagement_score - 0.5) * 0.1
                topic_pref["interest_level"] = max(0.1, min(1.0, 
                    topic_pref["interest_level"] + interest_change
                ))
            
            # Update metadata
            topic_pref["last_interaction"] = interaction.timestamp
            topic_pref["interaction_count"] += 1
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract potential topics from content.
        
        Args:
            content: Text content to analyze
            
        Returns:
            List of extracted topics
        """
        # This is a simple implementation - in a real system, you might use
        # more sophisticated NLP techniques
        
        # Common topics to look for
        common_topics = [
            "ai", "technology", "art", "design", "science", "ethics",
            "creativity", "innovation", "future", "philosophy", "education",
            "environment", "health", "business", "politics", "culture"
        ]
        
        # Extract topics that appear in content
        found_topics = []
        for topic in common_topics:
            if f" {topic} " in f" {content} ":
                found_topics.append(topic)
        
        return found_topics
    
    def _store_in_json_files(self, interaction: Interaction) -> None:
        """Store interaction in JSON files.
        
        Args:
            interaction: Interaction object to store
        """
        try:
            # Store interaction in individual file
            interaction_file = os.path.join(
                self.memory_dir, 
                "interactions", 
                f"{interaction.interaction_id}.json"
            )
            
            with open(interaction_file, 'w') as f:
                json.dump({
                    "interaction_id": interaction.interaction_id,
                    "interaction_type": interaction.interaction_type,
                    "user": interaction.user,
                    "content": interaction.content,
                    "timestamp": interaction.timestamp,
                    "sentiment": interaction.sentiment,
                    "engagement_score": interaction.engagement_score
                }, f, indent=2)
            
            # Update recent interactions file
            recent_file = os.path.join(self.memory_dir, "recent_interactions.json")
            recent_data = [
                {
                    "interaction_id": i.interaction_id,
                    "interaction_type": i.interaction_type,
                    "user": i.user,
                    "content": i.content,
                    "timestamp": i.timestamp,
                    "sentiment": i.sentiment,
                    "engagement_score": i.engagement_score
                } for i in self.short_term_memory
            ]
            with open(recent_file, 'w') as f:
                json.dump(recent_data, f, indent=2)
            
            # Update user relationships file
            if interaction.user != "self" and interaction.user in self.user_relationships:
                relationships_file = os.path.join(self.memory_dir, "relationships.json")
                with open(relationships_file, 'w') as f:
                    json.dump(self.user_relationships, f, indent=2)
            
            # Update topic preferences file
            topics_file = os.path.join(self.memory_dir, "topics.json")
            with open(topics_file, 'w') as f:
                json.dump(self.topic_preferences, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error storing interaction in JSON files: {e}")
    
    def get_recent_interactions(self, limit: int = 5) -> List[Interaction]:
        """Get most recent interactions from short-term memory.
        
        Args:
            limit: Maximum number of interactions to return
            
        Returns:
            List of recent Interaction objects (most recent ones, in chronological order)
        """
        # Step 1: First sort by timestamp (newest first) to get the most recent interactions
        most_recent = sorted(
            self.short_term_memory,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
        
        # Step 2: Then sort these most recent interactions by timestamp (oldest first) for chronological order
        # This ensures the returned list is in chronological order (oldest to newest)
        return sorted(
            most_recent,
            key=lambda x: x.timestamp
        )
    
    def get_user_relationship(self, username: str) -> Dict[str, Any]:
        """Get relationship information for a specific user.
        
        Args:
            username: Username to get relationship for
            
        Returns:
            Dictionary containing relationship information or default values if not found
        """
        default_relationship = {
            "familiarity": 0.0,
            "sentiment": 0.0,
            "last_interaction": time.time(),
            "interaction_count": 0
        }
        return self.user_relationships.get(username, default_relationship)
    
    def get_topic_preference(self, topic: str) -> Dict[str, Any]:
        """Get preference information for a specific topic.
        
        Args:
            topic: Topic to get preference for
            
        Returns:
            Dictionary containing topic preference or empty dict if not found
        """
        return self.topic_preferences.get(topic, {})
    
    def get_interactions_by_user(self, username: str) -> List[Interaction]:
        """Get interactions with a specific user.
        
        Args:
            username: Username to get interactions for
            
        Returns:
            List of Interaction objects with the specified user
        """
        return [i for i in self.short_term_memory if i.user == username]
    
    def update_user_relationship(self, username: str, familiarity: float = None, sentiment: float = None) -> None:
        """Update relationship with a user manually.
        
        Args:
            username: Username to update relationship for
            familiarity: Optional familiarity score (0.0 to 1.0)
            sentiment: Optional sentiment score (-1.0 to 1.0)
        """
        # Initialize relationship if not exists
        if username not in self.user_relationships:
            self.user_relationships[username] = {
                "familiarity": 0.0,
                "sentiment": 0.0,
                "last_interaction": time.time(),
                "interaction_count": 0
            }
        
        # Update values if provided
        if familiarity is not None:
            self.user_relationships[username]["familiarity"] = max(0.0, min(1.0, familiarity))
        
        if sentiment is not None:
            self.user_relationships[username]["sentiment"] = max(-1.0, min(1.0, sentiment))
        
        # Save to disk
        relationships_file = os.path.join(self.memory_dir, "relationships.json")
        with open(relationships_file, 'w') as f:
            json.dump(self.user_relationships, f, indent=2)
    
    def update_topic_preference(self, topic: str, interest_level: float = None, engagement_score: float = None) -> None:
        """Update preference for a topic manually.
        
        Args:
            topic: Topic to update preference for
            interest_level: Optional interest level (0.0 to 1.0)
            engagement_score: Optional engagement score (0.0 to 1.0)
        """
        # Initialize topic if not exists
        if topic not in self.topic_preferences:
            self.topic_preferences[topic] = {
                "interest_level": 0.5,
                "engagement_rate": 0.0,
                "engagement_score": 0.0,
                "last_interaction": time.time(),
                "interaction_count": 0
            }
        
        # Update values if provided
        if interest_level is not None:
            self.topic_preferences[topic]["interest_level"] = max(0.0, min(1.0, interest_level))
        
        if engagement_score is not None:
            self.topic_preferences[topic]["engagement_rate"] = max(0.0, min(1.0, engagement_score))
            self.topic_preferences[topic]["engagement_score"] = max(0.0, min(1.0, engagement_score))
        
        # Save to disk
        topics_file = os.path.join(self.memory_dir, "topics.json")
        with open(topics_file, 'w') as f:
            json.dump(self.topic_preferences, f, indent=2)
    
    def get_memory_context(self) -> Dict[str, Any]:
        """Get memory context for decision making.
        
        Returns:
            Dictionary containing memory context information
        """
        # Get recent interactions
        recent = self.get_recent_interactions(5)
        
        # Get top relationships (by familiarity)
        top_relationships = sorted(
            [(user, data) for user, data in self.user_relationships.items()],
            key=lambda x: x[1]["familiarity"],
            reverse=True
        )[:3]
        
        # Get top topics (by interest level)
        top_topics = sorted(
            [(topic, data) for topic, data in self.topic_preferences.items()],
            key=lambda x: x[1]["interest_level"],
            reverse=True
        )[:5]
        
        # Construct memory context
        context = {
            "recent_interactions": [
                {
                    "type": i.interaction_type,
                    "user": i.user,
                    "content": i.content[:100] + ("..." if len(i.content) > 100 else ""),
                    "time_ago": f"{int((time.time() - i.timestamp) / 60)} minutes ago"
                } for i in recent
            ],
            "relationships": {
                user: {
                    "familiarity": f"{data['familiarity']:.2f}",
                    "sentiment": f"{data['sentiment']:.2f}",
                    "interactions": data["interaction_count"]
                } for user, data in top_relationships
            },
            "interests": {
                topic: f"{data['interest_level']:.2f}"
                for topic, data in top_topics
            }
        }
        
        return context