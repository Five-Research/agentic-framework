# Twitter AI Agent 2.0 - Implementation Guide

This guide outlines how to implement and integrate the enhanced personality system into the existing Twitter AI Agent codebase.

## Overview

The enhanced personality system adds three key capabilities to the Twitter AI Agent:

1. **Emotion Modeling**: Dynamic emotional states that influence decision making
2. **Memory System**: Storage and retrieval of past interactions and relationships
3. **Learning Capabilities**: Adaptation of personality traits based on engagement metrics

## Implementation Steps

### 1. Update Dependencies

Add the following dependencies to `requirements.txt`:

```
sqlite3
nltk>=3.8.1
pandas>=2.0.0
```

### 2. Integrate Enhanced Personality System

#### Update Agent Configuration

Modify `twitter_agent/config.py` to support the enhanced personality schema:

```python
# In AgentConfig._load_personality method, update the default_personality:

default_personality = {
    "name": "Default AI",
    "bio": "I'm an AI exploring Twitter and sharing interesting thoughts.",
    "interests": ["technology", "AI", "creativity", "art", "science"],
    "tone": "friendly and curious",
    "posting_frequency": "medium",  # low, medium, high
    "interaction_style": "thoughtful",  # casual, thoughtful, professional
    "content_preferences": {
        "topics": ["AI", "technology", "creativity", "innovation"],
        "content_types": ["articles", "discussions", "questions"],
        "engagement_threshold": 0.7  # 0.0 to 1.0, higher means more selective
    },
    # New fields for enhanced personality system
    "emotional_state": {
        "base_state": "curious",
        "current_state": "curious",
        "intensity": 0.5,
        "triggers": {},
        "decay_rate": 0.1
    },
    "memory": {
        "short_term": {
            "capacity": 20,
            "decay_rate": 0.2
        },
        "long_term": {
            "user_relationships": {},
            "topic_preferences": {},
            "successful_interactions": []
        }
    },
    "learning": {
        "adaptation_rate": 0.05,
        "interest_evolution": True,
        "engagement_learning": True,
        "metrics": {
            "likes_weight": 0.3,
            "retweets_weight": 0.5,
            "replies_weight": 0.2,
            "impressions_weight": 0.1
        }
    }
}
```

#### Update TwitterAgent Class

Modify `twitter_agent/agent.py` to use the enhanced LLM interface:

```python
# Add import at the top
from twitter_agent.enhanced_llm import EnhancedLLMInterface

# In the _initialize_components method, replace the LLM initialization with:

# Initialize LLM interface
logger.info("Initializing Enhanced LLM interface...")
self.llm = EnhancedLLMInterface(
    api_key=self.config.openrouter_api_key,
    model=self.config.openrouter_model,
    personality=self.personality,
    personality_file_path=self.config.personality_file
)
```

#### Add Engagement Tracking

Add a method to the TwitterAgent class to track engagement metrics:

```python
def _track_engagement(self, post_content: str):
    """Track engagement metrics for a post.
    
    Args:
        post_content: Content of the post that was published
    """
    try:
        # Wait some time for initial engagement
        time.sleep(random.uniform(30, 60))
        
        # Get engagement metrics from Twitter
        metrics = self.browser.get_post_metrics()
        
        # Record in LLM interface
        self.llm.record_engagement(post_content, metrics)
        
        logger.info(f"Recorded engagement metrics: {metrics}")
        
    except Exception as e:
        logger.error(f"Error tracking engagement: {e}")
```

#### Update Browser Class

Add a method to the TwitterBrowser class to get post metrics:

```python
def get_post_metrics(self) -> Dict[str, int]:
    """Get engagement metrics for the most recent post.
    
    Returns:
        Dictionary containing engagement metrics
    """
    try:
        # This is a simplified implementation
        # In a real implementation, you would navigate to the post and extract metrics
        
        # For now, return placeholder metrics
        return {
            "likes": random.randint(0, 5),
            "retweets": random.randint(0, 2),
            "replies": random.randint(0, 3),
            "impressions": random.randint(10, 100)
        }
        
    except Exception as e:
        logger.error(f"Error getting post metrics: {e}")
        return {"likes": 0, "retweets": 0, "replies": 0, "impressions": 0}
```

#### Update Execute Action Method

Modify the `_execute_action` method to track engagement after posting:

```python
# In the _execute_action method, update the "post" case:

elif action_type == "post":
    # Create a new post
    content = action.get("content", "")
    success = self.browser.create_post(content)
    
    # If post was successful, track engagement
    if success:
        # Start a background thread to track engagement
        import threading
        thread = threading.Thread(target=self._track_engagement, args=(content,))
        thread.daemon = True
        thread.start()
```

### 3. Add Periodic Personality Adaptation

Add a method to periodically adapt the personality based on learning:

```python
def _adapt_personality(self):
    """Periodically adapt personality based on learning."""
    try:
        # Save current personality state
        self.llm.save_personality_state()
        logger.info("Adapted personality based on learning")
        
    except Exception as e:
        logger.error(f"Error adapting personality: {e}")
```

Add a call to this method in the main agent loop:

```python
# In the _run_agent_loop method, add:

# Track time since last adaptation
last_adaptation_time = time.time()

while datetime.now() < self.end_time:
    try:
        # Check if it's time to adapt personality (every 30 minutes)
        current_time = time.time()
        if current_time - last_adaptation_time > 1800:  # 30 minutes
            self._adapt_personality()
            last_adaptation_time = current_time
        
        # Rest of the existing loop code...
```

### 4. Update Main Script

Update `main.py` to ensure the logs directory exists:

```python
# In the main function, add before setup_logging:

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)
```

## Testing the Enhanced System

1. Create an enhanced personality profile (see `personalities/kiara_enhanced.json` for an example)
2. Run the agent with the enhanced profile:

```bash
python main.py --personality personalities/kiara_enhanced.json --duration 60
```

3. Monitor the logs to observe the emotional state changes, memory storage, and learning adaptations

## Next Steps

After implementing the enhanced personality system, consider these additional improvements:

1. Implement the advanced content creation features (media support, scheduling)
2. Add analytics and reporting capabilities
3. Develop a web interface for monitoring and controlling the agent
4. Expand to support multiple social media platforms

## Troubleshooting

- If the agent crashes with database errors, ensure SQLite is properly installed
- If emotional responses seem inappropriate, adjust the trigger thresholds in the personality file
- If memory usage grows too large, reduce the short-term memory capacity or implement pruning