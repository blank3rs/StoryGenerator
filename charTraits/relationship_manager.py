from typing import Dict, List, Optional
from .character import Character, Relationship

class RelationshipManager:
    @staticmethod
    def process_interaction(character1: Character, character2: Character, 
                          interaction_type: str, intensity: float = 0.1) -> None:
        """Process an interaction between two characters"""
        interaction_effects = {
            "positive": (0.1, 0.1),  # (trust, friendship)
            "negative": (-0.1, -0.1),
            "neutral": (0.0, 0.05),
            "conflict": (-0.15, -0.05),
            "cooperation": (0.15, 0.1),
            "betrayal": (-0.3, -0.2)
        }
        
        if interaction_type in interaction_effects:
            trust_change, friendship_change = interaction_effects[interaction_type]
            trust_change *= intensity
            friendship_change *= intensity
            
            # Update relationships both ways
            character1.update_relationship(character2.name, trust_change, friendship_change)
            character2.update_relationship(character1.name, trust_change, friendship_change)

    @staticmethod
    def get_relationship_summary(character: Character, other_character: str) -> str:
        """Get a summary of the relationship between two characters"""
        if other_character not in character.relationships:
            return f"{character.name} has no established relationship with {other_character}."
            
        rel = character.relationships[other_character]
        trust_level = "high" if rel.trust > 0.7 else "moderate" if rel.trust > 0.3 else "low"
        friendship_level = "strong" if rel.friendship > 0.7 else "moderate" if rel.friendship > 0.3 else "weak"
        
        return f"{character.name}'s relationship with {other_character}: {trust_level} trust, {friendship_level} friendship."
