import math
from charTraits.character import Character
from typing import Optional, Dict, Any

def calculate_stats(character):
    return {
        "intelligence": character.intelligence,
        "strength": character.strength,
        "charisma": character.charisma,
    }

def add_character(name: str, tribe: str, personality_traits: list[str], 
                 skills: Optional[list[str]] = None, 
                 memory: Optional[list[str]] = None) -> Dict[str, Any]:
    """Function to add a new character to the story with input validation"""
    # Input validation
    if not name or not isinstance(name, str):
        raise ValueError("Name must be a non-empty string")
    
    if not tribe or not isinstance(tribe, str):
        raise ValueError("Tribe must be a non-empty string")
    
    if not personality_traits or not isinstance(personality_traits, list):
        raise ValueError("Personality traits must be a non-empty list")
    
    # Ensure lists are properly formatted
    skills = skills if isinstance(skills, list) else ["Adaptability"]
    memory = memory if isinstance(memory, list) else ["I am new to this story"]
    
    # Create character with validated inputs
    try:
        new_character = Character(
            name=name.strip(),
            tribe=tribe.strip(),
            skills=skills,
            memory=memory,
            personality_traits=personality_traits
        )
        
        return {
            "name": new_character.name,
            "tribe": new_character.tribe,
            "personality_traits": new_character.personality_traits,
            "skills": new_character.skills,
            "memory": new_character.memory
        }
    except Exception as e:
        raise ValueError(f"Failed to create character: {str(e)}")

def add_to_memory(character: Character, memory_item: str) -> None:
    """Add a new memory to a character"""
    if not isinstance(memory_item, str) or not memory_item.strip():
        raise ValueError("Memory item must be a non-empty string")
    character.add_memory(memory_item.strip())
