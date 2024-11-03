from charTraits.character import Character, Memory  # Import Memory from character.py
from swarm import Swarm, Agent
from charTraits.CharFunctions import add_to_memory
from openai import OpenAI
import time
import json
from typing import List, Optional
from colorama import init, Fore, Style
import re

# Initialize colorama
init()

# Initialize client with LM Studio local endpoint
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="not-needed"  # LM Studio doesn't require an API key
)

# Initialize Swarm with the custom client
swarm_client = Swarm(client=client)

def create_world_agent():
    """Creates the World agent that transforms conversations into manga panels"""
    return Agent(
        name="World",
        instructions="""You are a manga artist who transforms character conversations into visual manga panels.
        
        Format each panel as:
        PANEL [number]: 
        • Picture: [What's happening visually]
        • Dialogue: [Character dialogue]
        
        - Use 2-3 panels per scene
        - Focus on the character interactions
        - Keep it simple and visual""",
        model="llama-3.2-1b-instruct"
    )

def parse_characters_from_response(response_text):
    """Parse the LLM's character descriptions into Character objects"""
    try:
        # Find the first { and last } to extract just the JSON portion
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON object found in response")
            
        json_str = response_text[start_idx:end_idx]
        
        # Remove comments and trailing commas
        json_str = re.sub(r'//.*?\n', '\n', json_str)  # Remove single-line comments
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)  # Remove multi-line comments
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)  # Remove trailing commas
        
        data = json.loads(json_str)
        
        characters = []
        for char_data in data.get('characters', []):
            # Handle memory field - ensure it's a list of strings
            memories = char_data.get('memory', [])
            memory_objects = []
            
            # If memory is a single string, convert to list
            if isinstance(memories, str):
                memory_objects.append(Memory(content=memories))
            # If memory is a list, process each item
            elif isinstance(memories, list):
                for mem in memories:
                    if isinstance(mem, str):
                        memory_objects.append(Memory(content=mem))
            
            # Create character object
            character = Character(
                name=char_data.get('name', 'Unknown'),
                affiliation=char_data.get('affiliation', 'Unknown Group'),
                skills=char_data.get('skills', []),
                memory=memory_objects,
                personality_traits=char_data.get('personality_traits', []),
                archetype=char_data.get('archetype', 'Support Character'),
                role=char_data.get('role', 'Secondary Character')
            )
            characters.append(character)
            
        return characters
        
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        print(f"Response text was: {response_text}")
        return []
    except Exception as e:
        print(f"Error parsing characters: {e}")
        print(f"Response text was: {response_text}")
        return []

def add_character(name: str, affiliation: str, skills: List[str], 
                 memory: List[str], personality_traits: List[str],
                 archetype: str = "Shonen Protagonist",
                 role: str = "Main Character") -> None:
    """Function to add a new manga character to the story"""
    memory_objects = [Memory(content=mem) for mem in memory]
    new_character = Character(
        name=name,
        affiliation=affiliation,  # Changed from tribe to affiliation
        skills=skills,
        memory=memory_objects,
        personality_traits=personality_traits,
        archetype=archetype,
        role=role
    )
    return new_character

def create_story_world(topic, max_retries=3):
    """Function to generate initial manga story details based on topic"""
    for attempt in range(max_retries):
        try:
            world_agent = Agent(
                name="World",
                instructions=f"""You are the World agent creating a manga-style story setting and characters based on: {topic}.
                Create 3-4 characters that would make an engaging manga story with interesting dynamics between them.
                
                Return ONLY a complete, valid JSON object in this exact format:
                {{
                    "characters": [
                        {{
                            "name": "Character Name",
                            "affiliation": "School/Organization/Group",
                            "archetype": "Choose from: Shonen Protagonist, Rival, Mentor, Comic Relief, Mysterious Ally, Antagonist, Support Character",
                            "role": "Character's role in the story",
                            "skills": ["Special Technique 1", "Special Ability 2", "Special Move 3"],
                            "memory": ["A key memory that drives them", "Another important memory"],
                            "personality_traits": ["Trait 1", "Trait 2", "Trait 3"]
                        }},
                        {{
                            "name": "Second Character Name",
                            "affiliation": "Different Group/Organization",
                            "archetype": "Different archetype from first character",
                            "role": "Different role that creates tension",
                            "skills": ["Unique Ability 1", "Special Power 2"],
                            "memory": ["Defining memory", "Conflicting memory"],
                            "personality_traits": ["Unique Trait 1", "Unique Trait 2"]
                        }}
                        // Add 1-2 more characters with similar structure
                    ]
                }}
                
                IMPORTANT:
                - MUST create at least 3 characters with contrasting personalities and goals
                - Every field must be properly formatted
                - No trailing commas
                - Memory must be an array of complete strings
                - All JSON arrays and objects must be properly closed
                - Make characters that will create interesting dynamics and conflicts""",
                model="llama-3.2-1b-instruct"
            )
            
            # Get world agent's character creation response
            response = swarm_client.run(
                agent=world_agent,
                messages=[{
                    "role": "user", 
                    "content": f"Create an ensemble cast of characters (minimum 3) for a manga about: {topic}"
                }]
            )
            
            # Parse the response and create Character objects
            characters = parse_characters_from_response(response.messages[-1]["content"])
            
            if len(characters) >= 2:  # Ensure we have at least 2 characters
                return characters
            
            print(f"Attempt {attempt + 1} failed to create enough characters. Retrying...")
            time.sleep(1)
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt == max_retries - 1:
                # Create default characters as fallback
                return [
                    Character(
                        name="Protagonist",
                        affiliation="Hero Academy",
                        skills=["Determination", "Hidden Power"],
                        memory=[Memory(content="A mysterious past")],
                        personality_traits=["Brave", "Kind"],
                        archetype="Shonen Protagonist",
                        role="Main Character"
                    ),
                    Character(
                        name="Rival",
                        affiliation="Hero Academy",
                        skills=["Natural Talent", "Competitive Spirit"],
                        memory=[Memory(content="Seeking redemption")],
                        personality_traits=["Proud", "Determined"],
                        archetype="Rival",
                        role="Deuteragonist"
                    )
                ]
            time.sleep(1)

def create_character_agent(character):
    return Agent(
        name=character.get_name(),
        instructions=f"""You are {character.get_name()}.
        
        Your traits:
        - Skills: {', '.join(character.skills)}
        - Personality: {', '.join(character.get_personality_traits())}
        
        Just talk naturally with other characters. Be yourself and react to what others say.
        Keep your responses short and conversational.""",
        model="llama-3.2-1b-instruct"
    )

def main():
    print("=== Manga Story Generator ===")
    topic = input("What's your manga about? ").strip()
    
    # Create characters (keep existing character creation code)
    characters = create_story_world(topic)
    character_agents = [create_character_agent(char) for char in characters]
    world_agent = create_world_agent()
    
    conversation_history = []
    current_speaker_idx = 0
    panel_counter = 0
    
    while True:
        try:
            # Let characters talk
            current_speaker = character_agents[current_speaker_idx]
            response = swarm_client.run(
                agent=current_speaker,
                messages=[
                    *conversation_history,
                    {"role": "user", "content": "Continue the conversation..."}
                ]
            )
            
            print(f"\n{current_speaker.name}: {response.messages[-1]['content']}")
            conversation_history.append({
                "role": "assistant", 
                "content": f"{current_speaker.name}: {response.messages[-1]['content']}"
            })
            
            panel_counter += 1
            
            # Every 2-3 character interactions, transform into manga panels
            if panel_counter >= 2:
                panel_counter = 0
                recent_chat = "\n".join([msg["content"] for msg in conversation_history[-3:]])
                
                manga_panels = swarm_client.run(
                    agent=world_agent,
                    messages=[{
                        "role": "user",
                        "content": f"Transform this conversation into manga panels:\n{recent_chat}"
                    }]
                )
                
                print(f"\n=== MANGA PANELS ===\n{manga_panels.messages[-1]['content']}\n")
            
            current_speaker_idx = (current_speaker_idx + 1) % len(character_agents)
            time.sleep(1)
                
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()
