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
    """Function to add a new character to the story"""
    new_character = Character(
        name=name,
        tribe=tribe,
        skills=skills or ["Adaptability"],
        memory=memory or ["I am new to this story"],
        personality_traits=personality_traits
    )
    
    return {
        "name": new_character.name,
        "tribe": new_character.tribe,
        "personality_traits": new_character.personality_traits,
        "skills": new_character.skills,
        "memory": new_character.memory
    }

def add_to_memory(character: Character, memory_item: str) -> None:
    """Add a new memory to a character"""
    character.add_memory(memory_item)
