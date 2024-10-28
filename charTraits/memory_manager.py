from typing import List, Optional
from datetime import datetime, timedelta
from .character import Memory, Character

class MemoryManager:
    @staticmethod
    def search_memories(character: Character, query: str, 
                       tags: Optional[List[str]] = None,
                       timeframe: Optional[timedelta] = None) -> List[Memory]:
        """Search character's memories based on content, tags, and timeframe"""
        results = []
        current_time = datetime.now()
        
        for memory in character.memory:
            # Check content match
            if query.lower() in memory.content.lower():
                # Check tags if specified
                if tags and not any(tag in memory.tags for tag in tags):
                    continue
                    
                # Check timeframe if specified
                if timeframe and (current_time - memory.timestamp) > timeframe:
                    continue
                    
                results.append(memory)
                
        return results

    @staticmethod
    def summarize_memories(character: Character, topic: Optional[str] = None) -> str:
        """Generate a summary of character's memories, optionally filtered by topic"""
        memories = character.memory
        if topic:
            memories = [m for m in memories if topic.lower() in m.content.lower()]
            
        if not memories:
            return f"{character.name} has no relevant memories."
            
        # Sort by importance and recency
        memories.sort(key=lambda x: (x.importance, x.timestamp), reverse=True)
        
        summary = f"{character.name}'s key memories:\n"
        for memory in memories[:5]:  # Top 5 memories
            summary += f"- {memory.content} (Importance: {memory.importance})\n"
            
        return summary
