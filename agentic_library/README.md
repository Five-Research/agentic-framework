# Agentic Library

A domain-agnostic library for adding emotion, learning, and memory capabilities to any LLM-based agent.

## Overview

The Agentic Library provides a framework for creating more dynamic, adaptive, and personalized AI agents across various application domains. By integrating emotion modeling, memory systems, and learning capabilities, agents can develop more authentic and engaging interactions with users.

## Key Features

- **Emotion Engine**: Dynamic emotional states that influence decision making
- **Memory System**: Short-term and long-term memory for storing and recalling interactions
- **Learning System**: Adaptation of personality traits and preferences based on engagement
- **Enhanced Personality**: Integration of emotion, memory, and learning into a cohesive system
- **LLM Interface**: Clean interface for interacting with any LLM provider

## Components

### Emotion Engine

The emotion engine models the dynamic emotional state of the agent, which influences decision making to create more authentic and engaging behavior. Emotions have different intensities and decay over time, returning to a base state.

```python
from agentic_library.emotion import EmotionEngine

# Initialize with a personality configuration
emotion_engine = EmotionEngine(personality)

# Update emotional state based on content
emotion_engine.update_emotion("I'm excited about the new AI developments!")

# Get current emotional state
emotion_state = emotion_engine.get_current_emotion()

# Get influence of current emotion on decision making
influence = emotion_engine.get_emotion_influence()
```

### Memory System

The memory system stores and retrieves memories of past interactions, builds relationships with users, and tracks topic preferences over time. It includes both short-term and long-term memory.

```python
from agentic_library.memory import MemorySystem, Interaction

# Initialize with a personality configuration
memory_system = MemorySystem(personality, db_path="memory.db")

# Store an interaction
interaction = Interaction(
    interaction_id="msg_123",
    interaction_type="message",
    user="user1",
    content="Hello, how are you?",
    timestamp=time.time()
)
memory_system.store_interaction(interaction)

# Get recent interactions
recent = memory_system.get_recent_interactions(limit=5)

# Get memory context for decision making
context = memory_system.get_memory_context()
```

### Learning System

The learning system adapts personality traits, interests, and behavior based on engagement metrics and interaction outcomes. It learns from successful patterns and evolves interests over time.

```python
from agentic_library.learning import LearningSystem, EngagementMetrics

# Initialize with a personality configuration
learning_system = LearningSystem(personality, personality_file_path="personality.json")

# Record engagement metrics
metrics = EngagementMetrics(
    positive_feedback=5,
    amplification=2,
    responses=3,
    impressions=100
)
engagement_score = learning_system.record_engagement(
    content="This is an interesting topic!",
    metrics=metrics,
    topics=["AI", "technology"]
)

# Get learning insights for decision making
insights = learning_system.get_learning_insights()

# Save updated personality to file
learning_system.save_personality()
```

### Enhanced Personality System

The enhanced personality system integrates emotion, memory, and learning capabilities to create a more dynamic and adaptive personality for any LLM-based agent.

```python
from agentic_library.enhanced_personality import EnhancedPersonalitySystem

# Initialize with a personality configuration
personality_system = EnhancedPersonalitySystem(
    personality,
    personality_file_path="personality.json",
    db_path="memory.db"
)

# Process content to update emotional state and memory
personality_system.process_content(content_items)

# Record an action taken by the agent
personality_system.record_action(action, result)

# Get context for decision making
context = personality_system.get_decision_context(current_content)

# Save the current state of the personality system
personality_system.save_state()
```

### LLM Interface

The LLM interface provides a clean interface for interacting with any LLM provider, leveraging the enhanced personality system for more dynamic and personalized responses.

```python
from agentic_library.openai_interface import OpenAIInterface

# Initialize with a personality configuration and API key
llm_interface = OpenAIInterface(
    personality=personality,
    api_key="your-api-key",
    model="gpt-4",
    personality_file_path="personality.json"
)

# Decide what action to take based on content
action = llm_interface.decide_action(current_content)

# Save the current state of the personality system
llm_interface.save_state()
```

## Getting Started

1. Install the library:

```bash
pip install agentic-library
```

2. Create a personality configuration file (see examples in the `personalities` directory)

3. Initialize the library components:

```python
from agentic_library.config import OpenAIAgentConfig
from agentic_library.openai_interface import OpenAIInterface

# Create agent configuration
config = OpenAIAgentConfig(
    api_key="your-api-key",
    model="gpt-4",
    personality_file="personality.json",
    memory_db_path="memory.db"
)

# Initialize the LLM interface
llm_interface = OpenAIInterface(
    personality=config.personality,
    api_key=config.api_key,
    model=config.model,
    personality_file_path=config.personality_file
)
```

4. Use the library to process content and make decisions:

```python
# Example content to process
content = [
    {
        "id": "1",
        "source": "user1",
        "text": "I've been thinking about the ethical implications of AI."
    }
]

# Decide on an action
action = llm_interface.decide_action(content)

# Handle the action
if action['type'] == 'message':
    print(f"Agent says: {action['content']}")
elif action['type'] == 'response':
    print(f"Agent responds to {action.get('to', 'user')}: {action['content']}")
```

## Examples

See the `examples` directory for complete examples of how to use the library.

## License

MIT