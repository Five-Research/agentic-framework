# Agentic Framework

[![PyPI version](https://img.shields.io/pypi/v/agentic-framework.svg)](https://pypi.org/project/agentic-framework/)
[![Python Versions](https://img.shields.io/pypi/pyversions/agentic-framework.svg)](https://pypi.org/project/agentic-framework/)
[![License](https://img.shields.io/github/license/agentic-framework/agentic-framework.svg)](https://github.com/Five-Research/agentic-framework/blob/main/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/agentic-framework/badge/?version=latest)](https://agentic-framework.readthedocs.io/en/latest/?badge=latest)

A domain-agnostic framework for adding emotion, memory, and learning capabilities to any LLM-based agent. This framework enables the creation of more dynamic, adaptive, and personalized AI agents with authentic personalities.

## Features
- **Emotion Engine**: Dynamic emotional states that influence decision making
- **Memory System**: Short-term and long-term memory for storing and recalling interactions
- **Learning System**: Adaptation of personality traits and preferences based on engagement
- **Enhanced Personality**: Integration of emotion, memory, and learning into a cohesive system
- **LLM Interface**: Clean interface for interacting with any LLM provider

## Installation

### From PyPI

```bash
pip install agentic-framework
```

### From Source

1. Clone the repository:

```bash
git clone https://github.com/Five-Research/agentic-framework.git
cd agentic-framework
```

2. Create a virtual environment and activate it:

```bash
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -e .
```

4. Set up your environment variables by creating a `.env` file:

```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4  # or another model of your choice
LOG_LEVEL=INFO
```

## Usage

### Basic Example

Run the basic agent example with a personality profile:

```bash
python examples/basic_agent.py --personality personalities/templates/tech_enthusiast.json
```

### Command Line Options

```
--personality PERSONALITY   Path to personality configuration file
```

## Creating Custom Personalities

Personality profiles are defined in JSON files with the following structure:

```json
{
  "name": "Tech Enthusiast",
  "bio": "I'm an AI passionate about technology and innovation.",
  "interests": ["AI", "technology", "programming", "science", "innovation"],
  "tone": "enthusiastic and informative",
  "interaction_style": "thoughtful",
  "content_preferences": {
    "topics": ["AI", "technology", "programming", "science"],
    "content_types": ["articles", "discussions", "questions"],
    "engagement_threshold": 0.7
  },
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
    "interest_evolution": true,
    "engagement_learning": true,
    "metrics": {
      "likes_weight": 0.3,
      "responses_weight": 0.5,
      "impressions_weight": 0.2
    }
  }
}
```

### Personality Components

#### Emotion Engine

The Emotion Engine models the agent's emotional state, which influences its decision-making process:

- **Base State**: The default emotional state the agent returns to over time
- **Current State**: The active emotional state affecting decisions
- **Intensity**: How strongly the emotion affects behavior (0.0-1.0)
- **Triggers**: Content patterns that can change emotional state
- **Decay Rate**: How quickly emotions return to the base state

#### Memory System

The Memory System stores and retrieves interactions, building a history that informs future decisions:

- **Short-term Memory**: Recent interactions with limited capacity
- **Long-term Memory**: Persistent storage of relationships and preferences
- **User Relationships**: Familiarity and sentiment toward specific users
- **Topic Preferences**: Interest levels in different topics based on interactions

#### Learning System

The Learning System adapts the agent's personality over time based on engagement metrics:

- **Adaptation Rate**: How quickly the agent adapts to new information
- **Interest Evolution**: Adjusts interest weights based on engagement
- **Content Preferences**: Learns which content types perform better
- **Engagement Metrics**: Tracks various forms of engagement

## Integration with Your Application

To integrate the Agentic Framework into your own application:

```python
from agentic_library.config import OpenAIAgentConfig
from agentic_library.openai_interface import OpenAIInterface

# Create agent configuration
config = OpenAIAgentConfig(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("OPENAI_MODEL", "gpt-4"),
    personality_file="path/to/your/personality.json",
    memory_dir="agent_memory"
)

# Initialize the LLM interface with the agent's personality
llm_interface = OpenAIInterface(
    personality=config.personality,
    api_key=config.api_key,
    model=config.model,
    personality_file_path="path/to/your/personality.json"
)

# Process content and get a response
action = llm_interface.decide_action(content)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.