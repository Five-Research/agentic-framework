# Humanized Agent Framework Guide

## Overview

The Humanized Agent Framework is a sophisticated system designed to create more authentic and engaging AI agents for social media interactions. Unlike traditional rule-based bots, this framework implements a dynamic personality system with emotions, memory, and learning capabilities that evolve over time based on interactions.

## Architecture

The framework is built with a modular architecture consisting of the following key components:

### Core Components

1. **Agent** - The main orchestrator that coordinates all components and handles the Twitter interaction loop
2. **Enhanced Personality System** - Integrates emotion, memory, and learning into a cohesive system
3. **Enhanced LLM Interface** - Provides context-aware prompting to the language model
4. **Browser Interface** - Handles the actual Twitter interactions

### Personality Components

1. **Emotion Engine** - Models dynamic emotional states that influence decision making
2. **Memory System** - Stores and retrieves past interactions and relationships
3. **Learning System** - Adapts personality traits and preferences based on engagement

## Component Details

### Emotion Engine

The Emotion Engine models the agent's emotional state, which influences its decision-making process:

- **Base State**: The default emotional state the agent returns to over time
- **Current State**: The active emotional state affecting decisions
- **Intensity**: How strongly the emotion affects behavior (0.0-1.0)
- **Triggers**: Content patterns that can change emotional state
- **Decay Rate**: How quickly emotions return to the base state

Emotions affect:
- Posting probability
- Engagement thresholds
- Content style and tone

### Memory System

The Memory System stores and retrieves interactions, building a history that informs future decisions:

- **Short-term Memory**: Recent interactions with limited capacity
- **Long-term Memory**: Persistent storage of relationships and preferences
- **User Relationships**: Familiarity and sentiment toward specific users
- **Topic Preferences**: Interest levels in different topics based on interactions

The system uses SQLite for persistent storage and provides context-relevant memories for decision making.

### Learning System

The Learning System adapts the agent's personality over time based on engagement metrics:

- **Adaptation Rate**: How quickly the agent adapts to new information
- **Interest Evolution**: Adjusts interest weights based on engagement
- **Content Preferences**: Learns which content types perform better
- **Engagement Metrics**: Tracks likes, retweets, replies, and impressions

The system periodically updates the personality file with learned adaptations.

### Enhanced Personality Integration

The Enhanced Personality System integrates the emotion, memory, and learning components:

- Processes feed content to update emotional state and memory
- Records agent actions in memory
- Tracks engagement metrics for learning
- Provides decision context to the LLM
- Generates prompt enhancements with personality insights

### Enhanced LLM Interface

The Enhanced LLM Interface communicates with the language model:

- Constructs context-aware system prompts
- Includes emotional state, memory insights, and learning patterns
- Parses LLM responses into actionable decisions
- Records engagement for learning

## Logic Flow

### Initialization Flow

1. Load personality configuration from file
2. Initialize emotion, memory, and learning systems
3. Set up database connections for persistent storage
4. Initialize browser and LLM interfaces

### Decision Making Flow

1. Agent fetches current Twitter feed
2. Feed content is processed by the personality system:
   - Emotion engine updates emotional state based on content
   - Memory system stores interactions and retrieves relevant memories
   - Learning system provides insights from past successful content
3. Enhanced personality system generates decision context
4. LLM interface constructs prompt with personality insights
5. LLM makes a decision based on the enhanced prompt
6. Agent executes the action on Twitter
7. Results are recorded for future learning

### Learning and Adaptation Flow

1. Agent records engagement metrics for posts
2. Learning system calculates engagement scores
3. Successful patterns are identified and stored
4. Periodically, the personality is adapted based on learning:
   - Interests are adjusted based on engagement
   - Content preferences are refined
   - Engagement thresholds are optimized
5. Updated personality is saved to file

## Personality Configuration

Personalities are defined in JSON files with the following structure:

```json
{
  "name": "Agent Name",
  "bio": "Agent description",
  "interests": ["topic1", "topic2"],
  "tone": "description of communication style",
  "posting_frequency": "high/medium/low",
  "interaction_style": "description of interaction approach",
  "content_preferences": {
    "topics": ["preferred topic1", "preferred topic2"],
    "content_types": ["type1", "type2"],
    "engagement_threshold": 0.5
  },
  "engagement_rules": {
    "like_posts_containing": ["keyword1", "keyword2"],
    "retweet_threshold": 0.7,
    "reply_style": "description of reply approach",
    "follow_users_interested_in": ["interest1", "interest2"]
  },
  "emotional_state": {
    "base_state": "neutral",
    "current_state": "curious",
    "intensity": 0.5,
    "triggers": {
      "trigger1": {"emotion": "excited", "intensity_modifier": 0.3}
    },
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
      "retweets_weight": 0.5,
      "replies_weight": 0.2,
      "impressions_weight": 0.1
    }
  }
}
```

## Usage

To run the agent:

```bash
python main.py --personality personalities/templates/tech_enthusiast.json --duration 60 --headless
```

Command line options:
- `--personality`: Path to personality JSON file
- `--duration`: Runtime in minutes
- `--headless`: Run browser in headless mode

## Extending the Framework

### Adding New Emotions

To add new emotions, extend the `EMOTION_INFLUENCES` dictionary in `emotion.py` with new entries following the existing pattern.

### Adding Learning Metrics

To track additional engagement metrics, extend the `EngagementMetrics` class in `learning.py` and update the `get_engagement_score` method.

### Creating Custom Personalities

Create new personality templates in the `personalities/templates` directory, following the JSON schema described above. Use the `PersonalityValidator` to ensure your template is valid.

## Best Practices

1. **Balanced Emotions**: Configure emotional triggers with varying intensities to create natural emotional dynamics
2. **Memory Capacity**: Adjust short-term memory capacity based on the complexity of interactions
3. **Adaptation Rate**: Use lower adaptation rates (0.01-0.05) for stable personalities, higher rates (0.1-0.2) for more adaptive ones
4. **Engagement Metrics**: Weight metrics based on the goals of your agent (e.g., prioritize replies for conversational agents)
5. **Regular Backups**: Periodically back up personality files to track evolution over time

## Troubleshooting

- **High CPU Usage**: Reduce short-term memory capacity or increase database query efficiency
- **Erratic Behavior**: Check emotional decay rate and lower intensity modifiers
- **Slow Learning**: Increase adaptation rate or adjust engagement thresholds
- **Database Errors**: Ensure proper permissions for the database file location

## Future Enhancements

1. **Emotional Contagion**: Allow agent to be influenced by the emotional tone of interactions
2. **Relationship Types**: Categorize relationships beyond simple familiarity and sentiment
3. **Content Generation Guidance**: Use learning insights to directly guide content generation
4. **Multi-platform Support**: Extend the framework to other social media platforms
5. **Collaborative Learning**: Share insights between multiple agent instances