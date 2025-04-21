"""Configuration module for the Agentic Library.

This module defines the configuration classes used by the agentic library components.
"""

import os
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any
from loguru import logger

from agentic_library.personality_validator import PersonalityValidator


@dataclass
class AgentConfig:
    """Configuration class for any LLM-based agent using the agentic library."""
    
    # Personality Configuration
    personality_file: Optional[str] = None
    
    # Optional directory path for memory system (JSON files)
    memory_dir: str = "memory"
    
    def __post_init__(self):
        """Validate configuration and load personality."""
        # Load personality configuration
        self.personality = self._load_personality()
    
    def _load_personality(self) -> Dict[str, Any]:
        """Load personality configuration from file or use default."""
        return PersonalityValidator.load_personality(
            self.personality_file if self.personality_file else "",
            enhanced=True
        )


@dataclass
class OpenAIAgentConfig(AgentConfig):
    """Configuration class for an agent using OpenAI."""
    
    # OpenAI Configuration
    api_key: str = ""
    model: str = "gpt-4"
    
    def __post_init__(self):
        """Validate configuration and load personality."""
        super().__post_init__()
        
        # Validate required fields
        if not self.api_key:
            raise ValueError("OpenAI API key is required")