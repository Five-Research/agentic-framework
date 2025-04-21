#!/bin/bash

# Run Tests Script for Agentic Framework
# This script provides various options for testing the agentic framework

set -e  # Exit on error

# Create necessary directories
mkdir -p logs

echo "Agentic Framework Testing"
echo "========================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "Installing test dependencies..."
    pip install pytest pytest-cov
fi

# Function to display help
show_help() {
    echo "Usage: ./run_tests.sh [option]"
    echo ""
    echo "Options:"
    echo "  all         Run all tests"
    echo "  unit        Run unit tests only"
    echo "  integration Run integration tests only"
    echo "  e2e         Run end-to-end tests only"
    echo "  coverage    Run tests with coverage report"
    echo "  demo        Run the interactive demo"
    echo "  help        Show this help message"
    echo ""
}

# Parse command line arguments
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

case "$1" in
    all)
        echo "Running all tests..."
        python -m pytest
        ;;
    unit)
        echo "Running unit tests..."
        python -m pytest tests/unit/
        ;;
    integration)
        echo "Running integration tests..."
        python -m pytest tests/integration/
        ;;
    e2e)
        echo "Running end-to-end tests..."
        python -m pytest tests/e2e/
        ;;
    coverage)
        echo "Running tests with coverage report..."
        python -m pytest --cov=agentic_library
        ;;
    demo)
        echo "Running interactive demo..."
        python tests/demo/agent_demo.py
        ;;
    help)
        show_help
        ;;
    *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
esac