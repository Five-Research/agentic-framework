# Testing Strategy for Agentic Framework

This directory contains tests for the Agentic Framework library. The testing strategy is designed to ensure that all components work correctly both individually and together.

## Test Structure

- `unit/`: Unit tests for individual components
  - `test_emotion.py`: Tests for the Emotion Engine
  - `test_memory.py`: Tests for the Memory System
  - `test_json_memory.py`: Tests for the JSON Memory implementation
  - `test_learning.py`: Tests for the Learning System
  - `test_personality_validator.py`: Tests for the Personality Validator

- `integration/`: Integration tests for combined components
  - `test_enhanced_personality.py`: Tests for the integrated personality system
  - `test_llm_interface.py`: Tests for the LLM interface with personality system

- `e2e/`: End-to-end tests for complete agent behavior
  - `test_basic_agent.py`: Tests for the basic agent example
  - `test_personality_adaptation.py`: Tests for personality adaptation over time

- `demo/`: Simple demo applications for manual testing
  - `emotion_demo.py`: Interactive demo of emotion engine
  - `memory_demo.py`: Interactive demo of memory system
  - `learning_demo.py`: Interactive demo of learning system
  - `agent_demo.py`: Complete agent demo with all systems

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
python -m pytest

# Run specific test category
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/e2e/

# Run with coverage report
python -m pytest --cov=agentic_library
```

## Test Data

The `test_data/` directory contains sample data for testing:
- Sample personality configurations
- Mock interaction data
- Expected outputs for various scenarios

## Continuous Integration

Consider setting up a CI pipeline to run these tests automatically on each commit.