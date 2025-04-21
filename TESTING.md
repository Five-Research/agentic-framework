# Testing Guide for Agentic Framework

This guide provides comprehensive instructions for testing the Agentic Framework library to ensure all components work correctly both individually and together.

## Automated Testing

The framework includes a comprehensive test suite with unit tests, integration tests, and end-to-end tests.

### Prerequisites

Install the required testing dependencies:

```bash
pip install pytest pytest-cov
```

### Running Tests

You can use the provided `run_tests.sh` script in the `tests` directory:

```bash
chmod +x tests/run_tests.sh  # Make the script executable (first time only)
./tests/run_tests.sh all      # Run all tests
```

Or run specific test categories:

```bash
./tests/run_tests.sh unit        # Run unit tests only
./tests/run_tests.sh integration  # Run integration tests only
./tests/run_tests.sh e2e          # Run end-to-end tests only
./tests/run_tests.sh coverage     # Run tests with coverage report
```

Alternatively, you can use pytest directly:

```bash
python -m pytest                # Run all tests
python -m pytest tests/unit/     # Run unit tests only
python -m pytest --cov=agentic_library  # Run with coverage report
```

## Manual Testing with Demo Application

The framework includes an interactive demo application that allows you to manually test the agent's behavior.

### Running the Demo

```bash
./tests/run_tests.sh demo
# or
python tests/demo/agent_demo.py
```

The demo provides two modes:
1. **Interactive Mode**: Chat with the agent directly and observe how it responds
2. **Demo Mode**: Run through predefined scenarios that showcase different aspects of the agent's personality

### What to Test Manually

When using the demo application, pay attention to these aspects:

1. **Emotional Responses**: Does the agent respond with appropriate emotions to different triggers?
   - Try using words like "amazing" to trigger excitement
   - Try using words like "problem" to trigger concern

2. **Memory System**: Does the agent remember previous interactions?
   - Refer to something you mentioned earlier and see if the agent recalls it
   - Interact multiple times as the same user to see if familiarity increases

3. **Learning System**: Does the agent adapt based on engagement?
   - Provide high engagement ratings for certain topics
   - After several interactions, check if those topics appear in the agent's interests

4. **Personality Integration**: Do all systems work together coherently?
   - Observe how emotional state affects responses
   - Check if memory of past interactions influences current responses
   - Verify that learning from engagement changes the agent's behavior over time

## Testing with Real LLM Providers

To test with actual LLM providers:

1. Ensure your `.env` file contains the necessary API keys:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   OPENROUTER_MODEL=deepseek/deepseek-r1:free
   ```

2. Run the demo application or create a custom test script that uses the OpenAIInterface

3. Monitor the agent's responses and verify they align with the personality configuration

## Testing Specific Components

### Emotion Engine

Test that the emotion engine correctly:
- Initializes with the personality's emotional state
- Updates emotions based on content triggers
- Decays emotions over time toward the base state
- Provides appropriate influence on decision making

### Memory System

Test that the memory system correctly:
- Stores and retrieves interactions
- Maintains short-term memory within capacity limits
- Builds and updates user relationships
- Tracks topic preferences
- Persists data between sessions

### Learning System

Test that the learning system correctly:
- Records engagement metrics
- Updates interests based on engagement
- Adapts tone based on engagement
- Saves personality changes to file

## Continuous Integration

Consider setting up a CI pipeline to run these tests automatically on each commit. This can be done using GitHub Actions, GitLab CI, or other CI/CD platforms.

## Security Testing

When testing with real credentials:
1. Never commit API keys to the repository
2. Verify that the agent doesn't log or expose sensitive information
3. Test with minimal permissions when possible

## Performance Testing

For applications that will handle significant traffic:
1. Test memory usage over extended sessions
2. Monitor API call frequency and costs
3. Evaluate response times under different loads

## Troubleshooting

If tests fail:
1. Check the logs in the `logs` directory
2. Verify that all dependencies are installed
3. Ensure API keys are valid if testing with real LLM providers
4. Check that the test directories have appropriate permissions