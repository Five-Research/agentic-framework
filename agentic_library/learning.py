"""Learning System Module

This module provides learning capabilities for any LLM-based agent,
allowing it to adapt its personality traits and preferences over time
based on engagement metrics and interaction outcomes.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from loguru import logger


@dataclass
class EngagementMetrics:
    """Represents engagement metrics for an interaction."""
    positive_feedback: int = 0  # e.g., likes, upvotes, positive reactions
    amplification: int = 0  # e.g., shares, retweets, reposts
    responses: int = 0  # e.g., replies, comments
    clicks: int = 0  # e.g., link clicks, detail views
    impressions: int = 0  # e.g., views, impressions
    timestamp: float = 0.0
    
    def get_engagement_score(self, weights: Dict[str, float]) -> float:
        """Calculate weighted engagement score.
        
        Args:
            weights: Dictionary of metric weights
            
        Returns:
            Weighted engagement score from 0.0 to 1.0
        """
        score = 0.0
        total_weight = sum(weights.values())
        
        if total_weight > 0:
            score += weights.get("positive_feedback", 0.0) * self.positive_feedback
            score += weights.get("amplification", 0.0) * self.amplification
            score += weights.get("responses", 0.0) * self.responses
            score += weights.get("clicks", 0.0) * self.clicks
            
            # Normalize by impressions if available
            if self.impressions > 0 and "impressions" in weights:
                score = score / self.impressions * weights["impressions"]
            
            # Normalize by total weight
            score = score / total_weight
        
        return min(1.0, max(0.0, score))


class LearningSystem:
    """Learning system for LLM-based agents.
    
    This class handles adaptation of personality traits, interests, and
    behavior based on engagement metrics and interaction outcomes.
    """
    
    # Default learning configuration if none specified in personality
    DEFAULT_LEARNING_CONFIG = {
        "adaptation_rate": 0.05,  # How quickly to adapt (0.0 to 1.0)
        "interest_evolution": True,  # Whether interests should evolve
        "engagement_learning": True,  # Whether to learn from engagement
        "metrics": {
            "positive_feedback_weight": 0.3,
            "amplification_weight": 0.5,
            "responses_weight": 0.2,
            "impressions_weight": 0.1
        }
    }
    
    def __init__(self, personality: Dict[str, Any], personality_file_path: Optional[str] = None):
        """Initialize the learning system with a personality configuration.
        
        Args:
            personality: Dictionary containing personality configuration
            personality_file_path: Path to personality file for saving changes
        """
        # Store the full personality configuration
        self.personality = personality
        self.personality_file_path = personality_file_path
        
        # Extract learning configuration or use defaults
        self.learning_config = personality.get("learning", self.DEFAULT_LEARNING_CONFIG)
        
        # Set adaptation rate
        self.adaptation_rate = self.learning_config.get("adaptation_rate", 0.05)
        
        # Feature flags
        self.interest_evolution = self.learning_config.get("interest_evolution", True)
        self.engagement_learning = self.learning_config.get("engagement_learning", True)
        
        # Metric weights for calculating engagement scores
        self.metric_weights = {
            "positive_feedback": self.learning_config.get("metrics", {}).get("positive_feedback_weight", 0.3),
            "amplification": self.learning_config.get("metrics", {}).get("amplification_weight", 0.5),
            "responses": self.learning_config.get("metrics", {}).get("responses_weight", 0.2),
            "impressions": self.learning_config.get("metrics", {}).get("impressions_weight", 0.1)
        }
        
        # Track successful patterns
        self.successful_patterns = self.learning_config.get("successful_patterns", [])
        
        # Track content performance by topic
        self.topic_performance = {}
        
        logger.info(f"Initialized learning system with adaptation rate: {self.adaptation_rate}")
    
    def record_engagement(self, content: str, metrics: EngagementMetrics, topics: List[str] = None) -> float:
        """Record engagement metrics for content and update learning.
        
        Args:
            content: The content that received engagement
            metrics: Engagement metrics object
            topics: List of topics associated with the content
            
        Returns:
            Engagement score from 0.0 to 1.0
        """
        if not self.engagement_learning:
            return 0.0
        
        # Calculate engagement score
        engagement_score = metrics.get_engagement_score(self.metric_weights)
        
        # Update topic performance if topics provided
        if topics and engagement_score > 0.0:
            self._update_topic_performance(topics, engagement_score)
        
        # Identify patterns in successful content
        if engagement_score > 0.7:
            self._identify_successful_patterns(content)
        
        # Update interests based on engagement
        if self.interest_evolution and topics:
            self._evolve_interests(topics, engagement_score)
        
        logger.debug(f"Recorded engagement with score: {engagement_score:.2f}")
        return engagement_score
    
    def _update_topic_performance(self, topics: List[str], engagement_score: float) -> None:
        """Update performance tracking for topics.
        
        Args:
            topics: List of topics associated with the content
            engagement_score: Calculated engagement score
        """
        # Initialize topic_engagement in personality if it doesn't exist
        if "topic_engagement" not in self.personality:
            self.personality["topic_engagement"] = {}
            
        for topic in topics:
            # Update internal topic performance tracking
            if topic not in self.topic_performance:
                self.topic_performance[topic] = {
                    "total_score": 0.0,
                    "count": 0,
                    "average": 0.0
                }
            
            # Update performance metrics in internal tracking
            perf = self.topic_performance[topic]
            perf["total_score"] += engagement_score
            perf["count"] += 1
            perf["average"] = perf["total_score"] / perf["count"]
            
            # Also update topic_engagement in personality
            if topic not in self.personality["topic_engagement"]:
                self.personality["topic_engagement"][topic] = {
                    "score": 0.0,
                    "count": 0
                }
            
            # Update topic engagement in personality
            topic_eng = self.personality["topic_engagement"][topic]
            topic_eng["score"] = (topic_eng["score"] * topic_eng["count"] + engagement_score) / (topic_eng["count"] + 1)
            topic_eng["count"] += 1
    
    def _identify_successful_patterns(self, content: str) -> None:
        """Identify patterns in successful content.
        
        Args:
            content: Content that received high engagement
        """
        # This is a simplified implementation - in a real system, you might use
        # more sophisticated NLP techniques to identify patterns
        
        # Look for phrases or patterns in successful content
        words = content.lower().split()
        
        # Check for question patterns
        if "?" in content:
            self._add_successful_pattern("questions", 0.1)
        
        # Check for exclamation patterns
        if "!" in content:
            self._add_successful_pattern("exclamations", 0.1)
        
        # Check for length patterns
        if len(words) < 10:
            self._add_successful_pattern("short_content", 0.1)
        elif len(words) > 30:
            self._add_successful_pattern("long_content", 0.1)
    
    def _add_successful_pattern(self, pattern: str, confidence: float) -> None:
        """Add or update a successful pattern.
        
        Args:
            pattern: Pattern identifier
            confidence: Confidence level in this pattern (0.0 to 1.0)
        """
        # Check if pattern already exists
        for existing in self.successful_patterns:
            if existing["pattern"] == pattern:
                # Update confidence with weighted average
                existing["confidence"] = (
                    existing["confidence"] * 0.8 + confidence * 0.2
                )
                existing["count"] += 1
                return
        
        # Add new pattern
        self.successful_patterns.append({
            "pattern": pattern,
            "confidence": confidence,
            "count": 1,
            "first_observed": time.time()
        })
    
    def _evolve_interests(self, topics: List[str], engagement_score: float) -> None:
        """Evolve interests based on engagement with topics.
        
        Args:
            topics: List of topics associated with the content
            engagement_score: Calculated engagement score
        """
        if "interests" not in self.personality:
            return
        
        # Get current interests
        current_interests = self.personality["interests"]
        
        # Calculate interest adjustment based on engagement
        adjustment = (engagement_score - 0.5) * self.adaptation_rate
        
        # For each topic that received engagement
        for topic in topics:
            # If topic is already an interest, adjust its position
            if topic in current_interests:
                # High engagement moves topic up in the list
                if adjustment > 0:
                    current_index = current_interests.index(topic)
                    if current_index > 0:
                        # Move up in the list (higher priority)
                        current_interests.remove(topic)
                        new_index = max(0, current_index - 1)
                        current_interests.insert(new_index, topic)
            # If topic is not an interest but got high engagement, consider adding it
            elif adjustment > 0.05 and len(current_interests) < 10:
                current_interests.append(topic)
                logger.debug(f"Added new interest: {topic}")
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from the learning system for decision making.
        
        Returns:
            Dictionary containing learning insights
        """
        # Get top performing topics
        top_topics = sorted(
            [(topic, data["average"]) for topic, data in self.topic_performance.items() if data["count"] > 2],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Get top successful patterns
        top_patterns = sorted(
            [(p["pattern"], p["confidence"]) for p in self.successful_patterns if p["count"] > 2],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Construct insights dictionary
        insights = {
            "top_performing_topics": dict(top_topics),
            "successful_patterns": dict(top_patterns),
            "interests": self.personality.get("interests", [])
        }
        
        return insights
    
    def update_interests(self) -> None:
        """Update interests based on engagement scores in topic_performance.
        
        This method analyzes topic engagement data and updates the agent's interests
        by adding high-engagement topics and potentially removing low-engagement ones.
        """
        if "interests" not in self.personality:
            return
            
        # Get current interests
        current_interests = self.personality["interests"]
        
        # Find high-engagement topics that aren't already interests
        for topic, data in self.topic_performance.items():
            # Only consider topics with sufficient data
            if data["count"] < 2:
                continue
                
            # If topic has high engagement and isn't an interest, add it
            if data["average"] > 0.7 and topic not in current_interests:
                current_interests.append(topic)
                logger.debug(f"Added new interest based on engagement: {topic}")
        
        # Save changes
        self.save_personality()
    
    def adapt_tone(self) -> None:
        """Adapt tone based on engagement data.
        
        This method analyzes tone engagement data and updates the agent's tone
        to the one with the highest engagement score.
        """
        if "tone" not in self.personality or "tone_engagement" not in self.personality:
            return
            
        # Get tone engagement data
        tone_engagement = self.personality["tone_engagement"]
        
        # Find tone with highest engagement score
        highest_score = 0.0
        best_tone = None
        
        for tone, data in tone_engagement.items():
            if data["score"] > highest_score and data["count"] >= 2:
                highest_score = data["score"]
                best_tone = tone
        
        # Update tone if a better one was found
        if best_tone and best_tone != self.personality["tone"]:
            self.personality["tone"] = best_tone
            logger.debug(f"Adapted tone to {best_tone} based on engagement")
            
            # Save changes
            self.save_personality()
    
    def save_personality(self) -> bool:
        """Save updated personality to file.
        
        Returns:
            True if save was successful, False otherwise
        """
        if not self.personality_file_path:
            logger.warning("No personality file path provided, cannot save")
            return False
        
        try:
            # Update learning configuration in personality
            self.personality["learning"]["successful_patterns"] = self.successful_patterns
            
            # Write updated personality to file
            with open(self.personality_file_path, 'w') as f:
                json.dump(self.personality, f, indent=2)
            
            logger.info(f"Saved updated personality to {self.personality_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving personality: {e}")
            return False