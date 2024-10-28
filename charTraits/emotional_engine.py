from typing import Dict, List, Optional
from .character import Character, Emotion

class EmotionalEngine:
    # Base emotions and their opposites
    EMOTION_PAIRS = {
        "joy": "sadness",
        "anger": "fear",
        "trust": "disgust",
        "anticipation": "surprise"
    }
    
    @staticmethod
    def process_event(character: Character, event: str, 
                     emotion_changes: Dict[str, float]) -> None:
        """Process an event and update character's emotional state"""
        for emotion, intensity_change in emotion_changes.items():
            current = character.emotions.get(emotion, Emotion(name=emotion)).intensity
            new_intensity = max(0.0, min(1.0, current + intensity_change))
            character.update_emotion(emotion, new_intensity)
            
            # Update opposite emotion
            if emotion in EmotionalEngine.EMOTION_PAIRS:
                opposite = EmotionalEngine.EMOTION_PAIRS[emotion]
                if opposite in character.emotions:
                    character.update_emotion(opposite, max(0.0, character.emotions[opposite].intensity - abs(intensity_change/2)))

    @staticmethod
    def get_dominant_emotion(character: Character) -> Optional[str]:
        """Get the character's current dominant emotion"""
        if not character.emotions:
            return None
            
        return max(character.emotions.items(), key=lambda x: x[1].intensity)[0]

    @staticmethod
    def calculate_mood(character: Character) -> float:
        """Calculate overall mood based on emotions"""
        if not character.emotions:
            return 0.5
            
        positive_emotions = ["joy", "trust", "anticipation"]
        negative_emotions = ["sadness", "fear", "disgust", "anger"]
        
        positive_sum = sum(character.emotions[e].intensity for e in positive_emotions if e in character.emotions)
        negative_sum = sum(character.emotions[e].intensity for e in negative_emotions if e in character.emotions)
        
        total_emotions = len([e for e in positive_emotions + negative_emotions if e in character.emotions])
        if total_emotions == 0:
            return 0.5
            
        return (positive_sum - negative_sum) / total_emotions + 0.5
