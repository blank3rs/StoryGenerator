from pydantic import BaseModel
from typing import List

class Character(BaseModel):
    name: str
    tribe: str
    skills: List[str]
    memory: List[str]
    personality_traits: List[str]

    def get_name(self) -> str:
        return self.name
    def get_tribe(self) -> str:
        return self.tribe

    def get_skills(self) -> List[str]:
        return self.skills

    def get_memory(self) -> List[str]:
        return self.memory

    def get_personality_traits(self) -> List[str]:
        return self.personality_traits
    
    def add_memory(self, memory_item: str) -> None:
        self.memory.append(memory_item)
