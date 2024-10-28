from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class Memory(BaseModel):
    content: str
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())
    importance: int = Field(default=1, ge=1, le=10)
    tags: List[str] = Field(default_factory=list)
    related_characters: List[str] = Field(default_factory=list)

    @classmethod
    def from_string(cls, content: str) -> 'Memory':
        """Create a Memory object from a string"""
        return cls(
            content=content,
            timestamp=datetime.now().timestamp(),
            importance=1,
            tags=[],
            related_characters=[]
        )

class Emotion(BaseModel):
    name: str
    intensity: float = Field(default=0.0, ge=0.0, le=1.0)
    
class Relationship(BaseModel):
    character_name: str
    trust: float = Field(default=0.5, ge=0.0, le=1.0)
    friendship: float = Field(default=0.5, ge=0.0, le=1.0)
    history: List[str] = Field(default_factory=list)

class Character(BaseModel):
    name: str
    tribe: str
    skills: List[str]
    memory: List[Memory] = Field(default_factory=list)
    personality_traits: List[str]
    emotions: Dict[str, Emotion] = Field(default_factory=dict)
    relationships: Dict[str, Relationship] = Field(default_factory=dict)
    beliefs: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    backstory: str = ""
    current_state: Dict[str, float] = Field(default_factory=lambda: {
        "energy": 1.0,
        "mood": 0.5,
        "health": 1.0
    })

    def add_memory(self, content: str, importance: int = 1, tags: List[str] = None, 
                  related_characters: List[str] = None) -> None:
        """Add a new memory with metadata"""
        memory = Memory(
            content=content,
            importance=importance,
            tags=tags or [],
            related_characters=related_characters or []
        )
        self.memory.append(memory)
        
    def get_recent_memories(self, limit: int = 5) -> List[Memory]:
        """Get most recent memories"""
        return sorted(self.memory, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_important_memories(self, min_importance: int = 7) -> List[Memory]:
        """Get memories above certain importance threshold"""
        return [m for m in self.memory if m.importance >= min_importance]

    def update_relationship(self, other_character: str, trust_change: float = 0, 
                          friendship_change: float = 0, event: Optional[str] = None) -> None:
        """Update relationship with another character"""
        if other_character not in self.relationships:
            self.relationships[other_character] = Relationship(character_name=other_character)
            
        rel = self.relationships[other_character]
        rel.trust = max(0.0, min(1.0, rel.trust + trust_change))
        rel.friendship = max(0.0, min(1.0, rel.friendship + friendship_change))
        
        if event:
            rel.history.append(event)

    def update_emotion(self, emotion: str, intensity: float) -> None:
        """Update character's emotional state"""
        if emotion not in self.emotions:
            self.emotions[emotion] = Emotion(name=emotion)
        self.emotions[emotion].intensity = max(0.0, min(1.0, intensity))

    def get_personality_summary(self) -> str:
        """Get a summary of character's personality"""
        return f"{self.name} is a {', '.join(self.personality_traits)} character from the {self.tribe} tribe."

    def get_name(self) -> str:
        return self.name

    def get_tribe(self) -> str:
        return self.tribe

    def get_personality_traits(self) -> List[str]:
        return self.personality_traits
