"""Enhanced LLM Interface Module

This module provides an interface to LLM providers for making decisions
based on the agent's personality, emotional state, memory, and learning insights.
"""

import json
from typing import Dict, Any, List, Optional

from loguru import logger

from agentic_library.enhanced_personality import EnhancedPersonalitySystem


class LLMInterface:
    """Interface to LLM providers for decision making.
    
    This class handles interactions with LLM providers to make decisions
    based on the agent's enhanced personality system, including emotions,
    memory, and learning capabilities.
    """
    
    def __init__(self, personality: Dict[str, Any], personality_file_path: Optional[str] = None):
        """Initialize the LLM interface.
        
        Args:
            personality: Dictionary containing personality configuration
            personality_file_path: Path to personality file for saving changes
        """
        self.personality = personality
        
        # Initialize enhanced personality system
        self.personality_system = EnhancedPersonalitySystem(personality, personality_file_path)
        
        logger.info(f"Initialized LLM interface for {personality['name']}")
    
    def set_llm_provider(self, provider: Any) -> None:
        """Set the LLM provider to use for generating responses.
        
        Args:
            provider: LLM provider instance (implementation-specific)
        """
        self.provider = provider
        logger.info(f"Set LLM provider: {type(provider).__name__}")
    
    def decide_action(self, current_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Decide what action to take based on enhanced personality and current content.
        
        Args:
            current_content: List of dictionaries containing content information
            
        Returns:
            Dictionary containing action type and parameters
        """
        # Get decision context from personality system
        context = self.personality_system.get_decision_context(current_content)
        
        # Construct prompt for the LLM
        prompt = self._construct_prompt(current_content, context)
        
        try:
            # Call LLM provider (implementation-specific)
            response = self._call_llm(prompt, context)
            
            # Parse the action from the response
            action = self._parse_action(response)
            
            # Record the action in the personality system
            self.personality_system.record_action(action)
            
            return action
            
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            # Return a default action if LLM call fails
            return {"type": "none", "reason": "LLM call failed"}
    
    def _construct_prompt(self, current_content: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """Construct a prompt for the LLM based on content and context.
        
        Args:
            current_content: List of dictionaries containing content information
            context: Decision context from personality system
            
        Returns:
            Prompt string for the LLM
        """
        # This is a template method that should be overridden by subclasses
        # to implement domain-specific prompt construction
        
        # Basic implementation
        personality = context["personality"]
        emotion = context["emotional_state"]
        memory = context["memory"]
        learning = context["learning"]
        
        prompt = f"""You are {personality['name']}, with the following traits:
- Bio: {self.personality.get('bio', 'No bio provided')}
- Interests: {', '.join(personality['interests'])}
- Tone: {personality['tone']}
- Interaction style: {personality['interaction_style']}

Your current emotional state is {emotion['current_emotion']} with intensity {emotion['intensity']:.2f}.

You have the following recent interactions in your memory:
"""
        
        # Add recent interactions
        for interaction in memory.get("recent_interactions", []):
            prompt += f"- {interaction['type']} with {interaction['user']}: {interaction['content']} ({interaction['time_ago']})"
        
        # Add current content to consider
        prompt += "\n\nYou are now looking at the following content:\n"
        for i, item in enumerate(current_content):
            prompt += f"{i+1}. From {item.get('source', 'unknown')}: {item.get('text', '')}\n"
        
        # Add action request
        prompt += "\nBased on your personality, emotional state, memory, and the current content, what action would you like to take? Choose from: message, response, none."
        
        return prompt
    
    def _call_llm(self, prompt: str, context: Dict[str, Any]) -> str:
        """Call the LLM provider with the constructed prompt.
        
        Args:
            prompt: Prompt string for the LLM
            context: Decision context from personality system
            
        Returns:
            Response string from the LLM
        """
        # This is a template method that should be overridden by subclasses
        # to implement provider-specific LLM calls
        
        # Check if provider is set
        if not hasattr(self, 'provider'):
            raise ValueError("LLM provider not set. Call set_llm_provider() first.")
        
        # Basic implementation (to be overridden)
        return "Not implemented"
    
    def _parse_action(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into an action dictionary.
        
        Args:
            response: Response string from the LLM
            
        Returns:
            Dictionary containing action type and parameters
        """
        # This is a template method that should be overridden by subclasses
        # to implement domain-specific action parsing
        
        # Basic implementation (to be overridden)
        return {"type": "none", "reason": "Action parsing not implemented"}
    
    def save_state(self) -> bool:
        """Save the current state of the personality system.
        
        Returns:
            True if save was successful, False otherwise
        """
        return self.personality_system.save_state()