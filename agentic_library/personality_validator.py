"""Personality Validator Module

This module provides validation functionality for personality templates,
ensuring they contain all required fields and follow the correct schema.
"""

import os
import json
import glob
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger


class PersonalityValidator:
    """Validator for personality templates.
    
    This class provides methods to validate personality templates against
    the required schema, ensuring all necessary fields are present and
    properly formatted.
    """
    
    # Required fields for basic personality
    BASIC_REQUIRED_FIELDS = [
        "name",
        "bio",
        "interests",
        "tone",
        "interaction_style",
        "content_preferences"
    ]
    
    # Required fields for enhanced personality
    ENHANCED_REQUIRED_FIELDS = BASIC_REQUIRED_FIELDS + [
        "emotional_state",
        "memory",
        "learning"
    ]
    
    # Required subfields for enhanced personality components
    REQUIRED_SUBFIELDS = {
        "emotional_state": ["base_state", "current_state", "intensity", "triggers", "decay_rate"],
        "memory": ["short_term", "long_term"],
        "learning": ["adaptation_rate", "interest_evolution", "engagement_learning", "metrics"]
    }
    
    @classmethod
    def validate_personality(cls, personality: Dict[str, Any], enhanced: bool = True) -> Tuple[bool, List[str]]:
        """Validate a personality dictionary against the required schema.
        
        Args:
            personality: Dictionary containing personality configuration
            enhanced: Whether to validate against enhanced personality schema
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Determine which required fields to check
        required_fields = cls.ENHANCED_REQUIRED_FIELDS if enhanced else cls.BASIC_REQUIRED_FIELDS
        
        # Check for required top-level fields
        for field in required_fields:
            if field not in personality:
                errors.append(f"Missing required field: {field}")
        
        # If enhanced, check required subfields
        if enhanced:
            for field, subfields in cls.REQUIRED_SUBFIELDS.items():
                if field in personality:
                    for subfield in subfields:
                        if subfield not in personality[field]:
                            errors.append(f"Missing required subfield: {field}.{subfield}")
        
        # Check content_preferences structure
        if "content_preferences" in personality:
            content_prefs = personality["content_preferences"]
            if not isinstance(content_prefs, dict):
                errors.append("content_preferences must be a dictionary")
            else:
                if "topics" not in content_prefs:
                    errors.append("Missing required field: content_preferences.topics")
                if "content_types" not in content_prefs:
                    errors.append("Missing required field: content_preferences.content_types")
        
        # Check emotional_state structure if enhanced
        if enhanced and "emotional_state" in personality:
            emotional_state = personality["emotional_state"]
            if "triggers" in emotional_state:
                triggers = emotional_state["triggers"]
                if not isinstance(triggers, dict):
                    errors.append("emotional_state.triggers must be a dictionary")
                else:
                    for trigger, trigger_data in triggers.items():
                        if not isinstance(trigger_data, dict):
                            errors.append(f"Trigger '{trigger}' must be a dictionary")
                        elif "emotion" not in trigger_data:
                            errors.append(f"Trigger '{trigger}' missing required field: emotion")
                        elif "intensity_modifier" not in trigger_data:
                            errors.append(f"Trigger '{trigger}' missing required field: intensity_modifier")
        
        return (len(errors) == 0, errors)
    
    @classmethod
    def generate_template(cls, enhanced: bool = True) -> Dict[str, Any]:
        """Generate a template personality configuration.
        
        Args:
            enhanced: Whether to generate an enhanced personality template
            
        Returns:
            Dictionary containing template personality configuration
        """
        # Basic personality template
        template = {
            "name": "Template Agent",
            "bio": "A template agent personality.",
            "interests": [
                "technology",
                "AI",
                "creativity"
            ],
            "tone": "friendly and helpful",
            "interaction_style": "thoughtful",
            "content_preferences": {
                "topics": [
                    "AI",
                    "technology",
                    "creativity"
                ],
                "content_types": [
                    "articles",
                    "discussions",
                    "questions"
                ],
                "engagement_threshold": 0.5
            }
        }
        
        # Add enhanced personality components if requested
        if enhanced:
            template["emotional_state"] = {
                "current_state": "curious",
                "intensity": 0.5,
                "base_state": "curious",
                "decay_rate": 0.1,
                "triggers": {
                    "AI": {
                        "emotion": "excited",
                        "intensity_modifier": 0.3
                    },
                    "ethics": {
                        "emotion": "thoughtful",
                        "intensity_modifier": 0.2
                    }
                }
            }
            
            template["memory"] = {
                "short_term": {
                    "capacity": 20,
                    "decay_rate": 0.2
                },
                "long_term": {
                    "user_relationships": {},
                    "topic_preferences": {},
                    "successful_interactions": []
                }
            }
            
            template["learning"] = {
                "adaptation_rate": 0.05,
                "interest_evolution": True,
                "engagement_learning": True,
                "metrics": {
                    "positive_feedback_weight": 0.3,
                    "amplification_weight": 0.5,
                    "responses_weight": 0.2,
                    "impressions_weight": 0.1
                },
                "successful_patterns": []
            }
        
        return template
    
    @classmethod
    def load_personality(cls, file_path: str, enhanced: bool = True) -> Dict[str, Any]:
        """Load and validate a personality from a file.
        
        Args:
            file_path: Path to personality JSON file
            enhanced: Whether to validate as enhanced personality
            
        Returns:
            Dictionary containing personality configuration or default if invalid
        """
        # Generate default personality using the validator
        default_personality = cls.generate_template(enhanced=enhanced)
        
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Personality file {file_path} not found, using default")
                return default_personality
            
            with open(file_path, 'r') as f:
                personality = json.load(f)
                
                # Validate the personality file
                is_valid, errors = cls.validate_personality(personality, enhanced=enhanced)
                if not is_valid:
                    logger.warning(f"Personality file {file_path} has validation errors:")
                    for error in errors:
                        logger.warning(f"  - {error}")
                    logger.warning("Using default personality instead")
                    return default_personality
                
                logger.info(f"Loaded personality: {personality.get('name', 'Unnamed')}")
                return personality
        except Exception as e:
            logger.error(f"Error loading personality file: {e}")
            logger.info("Using default personality instead")
            return default_personality