import json
import re
from typing import List
from .character import Character
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_characters_from_response(response_text: str) -> List[Character]:
    """
    Parse the LLM's character descriptions into Character objects.
    """
    characters = []
    
    # Clean up the response text to help with JSON parsing
    cleaned_text = cleanup_text(response_text)
    logger.info(f"Attempting to parse response: {cleaned_text[:200]}...")
    
    try:
        # Try to find and parse JSON content
        json_match = re.search(r'\{[\s\S]*\}', cleaned_text)
        if json_match:
            data = json.loads(json_match.group(0))
            char_list = data.get('characters', [])
            
            for char in char_list:
                try:
                    characters.append(Character(
                        name=char['name'],
                        tribe=char['tribe'],
                        skills=char['skills'],
                        memory=char['memory'],
                        personality_traits=char['personality_traits']
                    ))
                except KeyError as e:
                    logger.error(f"Missing required field in character data: {e}")
                    continue
                
    except json.JSONDecodeError:
        logger.warning("Failed to parse JSON, falling back to regex parsing")
        # Fallback to regex parsing
        char_blocks = re.split(r'\n(?=Character \d+:|Name:)', cleaned_text)
        
        for block in char_blocks:
            if not block.strip():
                continue
                
            try:
                char_dict = extract_character_info(block)
                if char_dict:
                    characters.append(Character(**char_dict))
            except Exception as e:
                logger.error(f"Error parsing character block: {e}")
                continue
    
    if not characters:
        logger.error("No characters could be parsed from the response")
        # Create a default character as fallback
        characters.append(Character(
            name="Default Character",
            tribe="Unknown",
            skills=["Adaptability"],
            memory=["I am a mysterious character"],
            personality_traits=["Mysterious"]
        ))
    
    return characters

def cleanup_text(text: str) -> str:
    """Clean up text to help with parsing"""
    # Remove any markdown formatting
    text = re.sub(r'```json\s*|\s*```', '', text)
    # Remove any leading/trailing whitespace
    text = text.strip()
    return text

def extract_character_info(block: str) -> dict:
    """Extract character information from a text block using regex"""
    patterns = {
        'name': r'Name:\s*(.+?)(?=\n|$)',
        'tribe': r'(?:Tribe|Group|Affiliation):\s*(.+?)(?=\n|$)',
        'skills': r'Skills:\s*\[?(.+?)\]?(?=\n|$)',
        'memory': r'Memory:\s*\[?(.+?)\]?(?=\n|$)',
        'personality_traits': r'(?:Personality Traits|Traits):\s*\[?(.+?)\]?(?=\n|$)'
    }
    
    result = {}
    for field, pattern in patterns.items():
        match = re.search(pattern, block, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            if field in ['skills', 'memory', 'personality_traits']:
                result[field] = parse_list(value)
            else:
                result[field] = value
        else:
            # Provide default values for missing fields
            if field == 'name':
                result[field] = "Unknown Character"
            elif field == 'tribe':
                result[field] = "Unknown Group"
            else:
                result[field] = []
    
    return result

def parse_list(text: str) -> List[str]:
    """Parse a comma-separated or list-like string into a list of strings"""
    # Remove brackets if present
    text = text.strip('[]')
    # Split by commas and clean up each item
    items = [item.strip().strip('"\'') for item in text.split(',')]
    # Filter out empty items
    return [item for item in items if item]
