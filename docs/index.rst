Welcome to Agentic Framework's documentation!
==========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   guide
   implementation_guide
   implementation_plan_personality_system
   version_2.0_features
   api/modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Overview
========

Agentic Framework is a domain-agnostic library for adding emotion, memory, and learning capabilities to any LLM-based agent. It enables the creation of more dynamic, adaptive, and personalized AI agents with authentic personalities.

Features
--------

- **Emotion Engine**: Dynamic emotional states that influence decision making
- **Memory System**: Short-term and long-term memory for storing and recalling interactions
- **Learning System**: Adaptation of personality traits and preferences based on engagement
- **Enhanced Personality**: Integration of emotion, memory, and learning into a cohesive system
- **LLM Interface**: Clean interface for interacting with any LLM provider

Installation
------------

From PyPI::

    pip install agentic-framework

From source::

    git clone https://github.com/agentic-framework/agentic-framework.git
    cd agentic-framework
    pip install -e .

Quick Start
-----------

.. code-block:: python

    from agentic_library.config import OpenAIAgentConfig
    from agentic_library.openai_interface import OpenAIInterface
    import os
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

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
    action = llm_interface.decide_action("Hello, how are you today?")
    print(action)