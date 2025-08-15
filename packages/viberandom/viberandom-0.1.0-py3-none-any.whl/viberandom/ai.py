import os
import random
from typing import Any, Optional
import google.generativeai as genai
from pydantic import BaseModel


class RandomVibeRequest(BaseModel):
    min_value: int
    max_value: int
    vibe: str
    count: int = 1


class RandomVibeResponse(BaseModel):
    numbers: list[int]


def configure_gemini() -> None:
    """Configure Gemini API with environment variable."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    genai.configure(api_key=api_key)


def viberandom(min_value: int = 1, max_value: int = 100, vibe: str = "random", count: int = 1) -> list[int]:
    """
    Generate random numbers with a specific vibe using Gemini Flash.
    
    Args:
        min_value: Minimum value for random numbers
        max_value: Maximum value for random numbers  
        vibe: The vibe/feeling for the numbers (e.g., "lucky", "chaotic", "peaceful", "energetic")
        count: How many numbers to generate
        
    Returns:
        List of integers that match the requested vibe
    """
    try:
        configure_gemini()
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Generate {count} random number(s) between {min_value} and {max_value} that have a "{vibe}" vibe.
        
        Think about what numbers would feel "{vibe}" and choose accordingly.
        For example:
        - "lucky" might favor numbers like 7, 77, 888
        - "chaotic" might prefer irregular, unexpected numbers
        - "peaceful" might lean toward round, harmonious numbers
        - "energetic" might choose higher, more dynamic numbers
        
        Return ONLY a JSON object in this exact format:
        {{"numbers": [number1, number2, ...]}}
        
        Make sure all numbers are integers between {min_value} and {max_value}.
        """
        
        response = model.generate_content(prompt)
        
        # Extract JSON from response
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
            
        # Parse the response
        import json
        result = json.loads(response_text)
        numbers = result.get("numbers", [])
        
        # Validate numbers are in range
        validated_numbers = []
        for num in numbers:
            if isinstance(num, int) and min_value <= num <= max_value:
                validated_numbers.append(num)
                
        # If we don't have enough valid numbers, fill with regular random
        while len(validated_numbers) < count:
            validated_numbers.append(random.randint(min_value, max_value))
            
        return validated_numbers[:count]
        
    except Exception as e:
        # Fallback to regular random if AI fails
        print(f"AI generation failed ({e}), falling back to regular random")
        return [random.randint(min_value, max_value) for _ in range(count)]


def viberandom_single(min_value: int = 1, max_value: int = 100, vibe: str = "random") -> int:
    """Generate a single random number with vibe."""
    return viberandom(min_value, max_value, vibe, 1)[0]