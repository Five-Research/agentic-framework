"""Memory System Module

This module provides memory capabilities for any LLM-based agent,
allowing it to store and recall past interactions and develop relationships with users.
"""

import os
import json
import time
import sqlite3
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
    """Memory system for LLM-based agents.
    
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
    
    def __init__(self, personality: Dict[str, Any], db_path: str = "memory.db"):
        """Initialize the memory system with a personality configuration.
        
        Args:
            personality: Dictionary containing personality configuration
            db_path: Path to SQLite database file for persistent storage
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
        
        # Set up database for persistent storage
        self.db_path = db_path
        self._initialize_database()
        
        logger.info(f"Initialized memory system with capacity: {self.short_term_capacity}")
    
    def _initialize_database(self) -> None:
        """Initialize the SQLite database for persistent memory storage."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables if they don't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    interaction_id TEXT PRIMARY KEY,
                    interaction_type TEXT,
                    user TEXT,
                    content TEXT,
                    timestamp REAL,
                    sentiment REAL,
                    engagement_score REAL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_relationships (
                    username TEXT PRIMARY KEY,
                    familiarity REAL,
                    sentiment REAL,
                    last_interaction REAL,
                    interaction_count INTEGER
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topic_preferences (
                    topic TEXT PRIMARY KEY,
                    interest_level REAL,
                    engagement_rate REAL,
                    last_interaction REAL,
                    interaction_count INTEGER
                )
            """)
            
            conn.commit()
            conn.close()
            logger.debug("Memory database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing memory database: {e}")
    
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
                reverse=True
            )[:self.short_term_capacity]
        
        # Update user relationship
        self._update_user_relationship(interaction)
        
        # Update topic preferences based on content
        self._update_topic_preferences(interaction)
        
        # Store in database for long-term persistence
        self._store_in_database(interaction)
        
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
        # This is a simple implementation - in a real system, we might use
        # NLP techniques to extract topics more accurately
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
    
    def _store_in_database(self, interaction: Interaction) -> None:
        """Store interaction in SQLite database.
        
        Args:
            interaction: Interaction object to store
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store interaction
            cursor.execute("""
                INSERT OR REPLACE INTO interactions
                (interaction_id, interaction_type, user, content, timestamp, sentiment, engagement_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                interaction.interaction_id,
                interaction.interaction_type,
                interaction.user,
                interaction.content,
                interaction.timestamp,
                interaction.sentiment,
                interaction.engagement_score
            ))
            
            # Update user relationship
            if interaction.user != "self" and interaction.user in self.user_relationships:
                rel = self.user_relationships[interaction.user]
                cursor.execute("""
                    INSERT OR REPLACE INTO user_relationships
                    (username, familiarity, sentiment, last_interaction, interaction_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    interaction.user,
                    rel["familiarity"],
                    rel["sentiment"],
                    rel["last_interaction"],
                    rel["interaction_count"]
                ))
            
            # Update topic preferences
            for topic, pref in self.topic_preferences.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO topic_preferences
                    (topic, interest_level, engagement_rate, last_interaction, interaction_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    topic,
                    pref["interest_level"],
                    pref["engagement_rate"],
                    pref["last_interaction"],
                    pref["interaction_count"]
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing interaction in database: {e}")
    
    def get_recent_interactions(self, limit: int = 5) -> List[Interaction]:
        """Get most recent interactions from short-term memory.
        
        Args:
            limit: Maximum number of interactions to return
            
        Returns:
            List of recent Interaction objects
        """
        # Sort by timestamp (newest first) and return limited number
        return sorted(
            self.short_term_memory,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
    
    def get_user_relationship(self, username: str) -> Dict[str, Any]:
        """Get relationship information for a specific user.
        
        Args:
            username: Username to get relationship for
            
        Returns:
            Dictionary containing relationship information or empty dict if not found
        """
        return self.user_relationships.get(username, {})
    
    def get_topic_preference(self, topic: str) -> Dict[str, Any]:
        """Get preference information for a specific topic.
        
        Args:
            topic: Topic to get preference for
            
        Returns:
            Dictionary containing topic preference or empty dict if not found
        """
        return self.topic_preferences.get(topic, {})
    
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