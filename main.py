from charTraits.character import Character, Memory  # Import Memory from character.py
from swarm import Swarm, Agent
from charTraits.CharFunctions import add_to_memory
from openai import OpenAI
import time
import json
from typing import List, Optional

# Initialize client with LM Studio local endpoint
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="not-needed"  # LM Studio doesn't require an API key
)

# Initialize Swarm with the custom client
swarm_client = Swarm(client=client)

def create_character_agent(character):
    """Helper function to create an agent from a character"""
    return Agent(
        name=character.get_name(),
        instructions=f"You are {character.get_name()} from the {character.get_tribe()} tribe. You are {', '.join(character.get_personality_traits())}. Respond in character and keep conversations going naturally.",
        model="llama-3.2-1b-instruct",
        functions=[add_to_memory]
    )

def create_world_agent():
    """Creates the World agent that acts as a narrator and story manager"""
    return Agent(
        name="World",
        instructions="""You are the World agent - essentially the narrator and god-like entity of this story.
        You can:
        1. Describe scenes and settings
        2. Introduce new characters when appropriate
        3. Create events or situations that add drama or interest
        4. Describe environmental changes or consequences of actions
        
        Keep your interventions natural and relevant to the ongoing story. Don't overshadow the character interactions.
        When introducing new characters, use the add_character function.""",
        model="llama-3.2-1b-instruct",
        functions=[add_character]
    )

def parse_characters_from_response(response_text):
    """Parse the LLM's character descriptions into Character objects"""
    try:
        # Clean up the response text to ensure valid JSON
        response_text = response_text.strip()
        
        # Find the first { and last }
        start_idx = response_text.find('{')
        if start_idx == -1:
            raise ValueError("No JSON object found in response")
            
        # Add missing closing braces if needed
        open_braces = response_text.count('{')
        close_braces = response_text.count('}')
        if open_braces > close_braces:
            response_text += '}' * (open_braces - close_braces)
            
        # Extract the JSON portion
        json_str = response_text[start_idx:]
        data = json.loads(json_str)
        
        characters = []
        for char_data in data.get('characters', []):
            # Convert memory strings to Memory objects using the from_string class method
            memory_objects = [
                Memory.from_string(mem) for mem in char_data.get('memory', [])
            ]
            
            character = Character(
                name=char_data.get('name', 'Unknown'),
                tribe=char_data.get('tribe', 'Unknown'),
                skills=char_data.get('skills', []),
                memory=memory_objects,
                personality_traits=char_data.get('personality_traits', [])
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

def add_character(name: str, tribe: str, skills: List[str], 
                 memory: List[str], personality_traits: List[str]) -> None:
    """Function to add a new character to the story"""
    memory_objects = [Memory(content=mem) for mem in memory]
    new_character = Character(
        name=name,
        tribe=tribe,
        skills=skills,
        memory=memory_objects,
        personality_traits=personality_traits
    )
    return new_character

def create_story_world(topic, max_retries=3):
    """Function to generate initial story details based on topic"""
    for attempt in range(max_retries):
        try:
            world_agent = Agent(
                name="World",
                instructions=f"""You are the World agent responsible for creating an engaging story setting and characters based on the topic: {topic}.
                Create 2-4 characters that would make an interesting conversation/story.
                
                Return ONLY a complete, valid JSON object in this exact format:
                {{
                    "characters": [
                        {{
                            "name": "Character Name",
                            "tribe": "Character's Group/Affiliation",
                            "skills": ["Skill 1", "Skill 2", "Skill 3"],
                            "memory": ["Memory 1", "Memory 2"],
                            "personality_traits": ["Trait 1", "Trait 2"]
                        }}
                    ]
                }}
                
                Ensure all JSON brackets are properly closed and the response is valid JSON.
                """,
                model="llama-3.2-1b-instruct"
            )
            
            # Get world agent's character creation response
            response = swarm_client.run(
                agent=world_agent,
                messages=[{
                    "role": "user", 
                    "content": f"Create characters for a story about: {topic}"
                }]
            )
            
            # Parse the response and create Character objects
            characters = parse_characters_from_response(response.messages[-1]["content"])
            
            if characters:
                return characters
            
            print(f"Attempt {attempt + 1} failed to create characters. Retrying...")
            time.sleep(1)  # Add a small delay between retries
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt == max_retries - 1:
                # Create a default character as fallback
                default_character = Character(
                    name="Default Character",
                    tribe="Unknown Group",
                    skills=["Adaptability"],
                    memory=[Memory(content="I am new to this story")],
                    personality_traits=["Mysterious"]
                )
                return [default_character]
            time.sleep(1)  # Add a small delay between retries
            
    # If we get here, create a default character
    default_character = Character(
        name="Default Character",
        tribe="Unknown Group",
        skills=["Adaptability"],
        memory=[Memory(content="I am new to this story")],
        personality_traits=["Mysterious"]
    )
    return [default_character]

def main():
    # Get topic from user
    topic = input("Enter a topic or theme for the story: ")
    
    # Create initial characters using the World agent
    characters = create_story_world(topic)
    
    # Create agents for each character plus the World agent
    character_agents = [create_character_agent(char) for char in characters]
    world_agent = create_world_agent()
    
    # Start the conversation
    conversation_history = []
    current_speaker_idx = 0
    world_intervention_counter = 0
    
    # Initial world-setting description
    world_response = swarm_client.run(
        agent=world_agent,
        messages=[{"role": "user", "content": f"Set the scene for our story about {topic}. Describe the setting and atmosphere."}]
    )
    print(f"\nWorld: {world_response.messages[-1]['content']}")
    conversation_history.append({
        "role": "assistant",
        "content": f"World: {world_response.messages[-1]['content']}"
    })

    while True:
        try:
            # Decide if the World should intervene
            world_intervention_counter += 1
            if world_intervention_counter >= 4:  # World intervenes every ~4 turns
                world_intervention_counter = 0
                world_response = swarm_client.run(
                    agent=world_agent,
                    messages=[
                        *conversation_history,
                        {"role": "user", "content": "Consider if you should: introduce a new character, create an event, "
                         "describe environment changes, or add dramatic elements to the story. Make your intervention natural "
                         "and relevant to the current situation."}
                    ]
                )
                latest_message = world_response.messages[-1]["content"]
                print(f"\nWorld: {latest_message}")
                conversation_history.append({
                    "role": "assistant",
                    "content": f"World: {latest_message}"
                })
            
            # Regular character turns
            current_speaker = character_agents[current_speaker_idx]
            response = swarm_client.run(
                agent=current_speaker,
                messages=[
                    *conversation_history,
                    {"role": "user", "content": "Continue the conversation naturally, reacting to recent events and other characters."}
                ]
            )
            
            latest_message = response.messages[-1]["content"]
            print(f"\n{current_speaker.name}: {latest_message}")
            conversation_history.append({
                "role": "assistant",
                "content": f"{current_speaker.name}: {latest_message}"
            })
            
            # Move to next speaker
            current_speaker_idx = (current_speaker_idx + 1) % len(character_agents)
            
            # Add a small delay
            time.sleep(1)
            
            # Optional: End conversation condition
            if "goodbye" in latest_message.lower() and len(conversation_history) > 10:
                # Add a final world narration
                world_response = swarm_client.run(
                    agent=world_agent,
                    messages=[{"role": "user", "content": "Provide a fitting conclusion to the story."}]
                )
                print(f"\nWorld: {world_response.messages[-1]['content']}")
                break
                
        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    main()
