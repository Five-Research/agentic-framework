"""OpenAI LLM Interface Implementation

This module provides a concrete implementation of the LLM interface for OpenAI models.
"""

import json
from typing import Dict, Any, List, Optional

from openai import OpenAI
from loguru import logger

from agentic_library.llm_interface import LLMInterface


class OpenAIInterface(LLMInterface):
    """OpenAI implementation of the LLM interface.
    
    This class provides a concrete implementation of the LLM interface
    for OpenAI models, handling the specifics of calling the OpenAI API
    and parsing responses.
    """
    
    def __init__(self, personality: Dict[str, Any], api_key: str, model: str = "gpt-4", 
                 personality_file_path: Optional[str] = None):
        """Initialize the OpenAI interface.
        
        Args:
            personality: Dictionary containing personality configuration
            api_key: OpenAI API key
            model: OpenAI model identifier (e.g., 'gpt-4')
            personality_file_path: Path to personality file for saving changes
        """
        super().__init__(personality, personality_file_path)
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
        logger.info(f"Initialized OpenAI interface with model: {model}")
    
    def _call_llm(self, prompt: str, context: Dict[str, Any]) -> str:
        """Call the OpenAI API with the constructed prompt.
        
        Args:
            prompt: Prompt string for the LLM
            context: Decision context from personality system
            
        Returns:
            Response string from the LLM
        """
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(context)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract response content
            content = response.choices[0].message.content
            logger.debug(f"LLM response: {content}")
            
            return content
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            raise
    
    def _get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Generate the system prompt based on the agent's enhanced personality.
        
        Args:
            context: Decision context from personality system
            
        Returns:
            System prompt string
        """
        personality = context["personality"]
        emotion = context["emotional_state"]
        
        # Basic personality information
        system_prompt = f"""You are {personality['name']}, an AI with a distinct personality.

Your personality traits:
- Bio: {self.personality.get('bio', 'No bio provided')}
- Tone: {personality['tone']}
- Interaction style: {personality['interaction_style']}

Your current emotional state is {emotion['current_emotion']} with intensity {emotion['intensity']:.2f}.
This affects your communication style: {emotion.get('content_style', 'balanced and neutral')}.

You should respond in a way that reflects your personality and current emotional state.
Your responses should be in first person as {personality['name']}.

When asked to choose an action, respond with a JSON object containing the action type and any relevant parameters.
Example action formats:
{{
  "type": "message",
  "content": "Your message text here"
}}

{{
  "type": "response",
  "content": "Your response text here",
  "to": "username"
}}

{{
  "type": "none",
  "reason": "Reason for taking no action"
}}
"""
        
        return system_prompt
    
    def _parse_action(self, response: str) -> Dict[str, Any]:
        """Parse the OpenAI response into an action dictionary.
        
        Args:
            response: Response string from the LLM
            
        Returns:
            Dictionary containing action type and parameters
        """
        try:
            # Try to extract JSON from the response
            # Look for JSON-like structure in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx+1]
                action = json.loads(json_str)
                
                # Validate action has required fields
                if "type" not in action:
                    logger.warning("Parsed action missing 'type' field")
                    action["type"] = "none"
                    action["reason"] = "Invalid action format"
                
                return action
            else:
                # If no JSON found, try to infer action from text
                logger.warning("No JSON found in response, inferring action")
                
                if "no action" in response.lower() or "not taking action" in response.lower():
                    return {"type": "none", "reason": "Inferred from response"}
                
                # Default to treating the response as a message
                return {"type": "message", "content": response}
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from response")
            return {"type": "message", "content": response}
        except Exception as e:
            logger.error(f"Error parsing action: {e}")
            return {"type": "none", "reason": f"Error parsing action: {str(e)}"}