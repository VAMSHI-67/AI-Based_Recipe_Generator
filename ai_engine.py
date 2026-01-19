import os
import json
import google.generativeai as genai
from typing import Optional, Dict, List

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY environment variable not set!")

genai.configure(api_key=API_KEY)


def get_available_model():
    """
    Get the first available generative model from Gemini API.
    """
    try:
        # List all available models
        models = genai.list_models()
        for model in models:
            # Find a model that supports generateContent
            if "generateContent" in model.supported_generation_methods:
                return model.name.split("/")[-1]  # Extract model name
        
        # Fallback to gemini-pro if no model found
        return "gemini-pro"
    except Exception:
        # If listing fails, default to gemini-pro
        return "gemini-pro"


def generate_recipe_with_gemini(
    user_ingredients: List[str],
    meal_type: str,
    cuisine: str,
    cooking_time: int
) -> Optional[Dict]:
    """
    Use Gemini AI to generate a recipe from scratch based on user preferences.
    
    Args:
        user_ingredients: Normalized list of user ingredients
        meal_type: Selected meal type
        cuisine: Selected cuisine
        cooking_time: Available cooking time
    
    Returns:
        Dictionary with generated recipe details, or None on failure
    """
    
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables!")
    
    # Build concise prompt to save tokens
    prompt = f"""Generate a {cuisine} {meal_type.lower()} recipe using these ingredients: {', '.join(user_ingredients)}.
Cooking time: {cooking_time} minutes maximum.

Create a realistic recipe that:
1. Uses MOST of the given ingredients
2. Fits within the time limit
3. Is a {cuisine} {meal_type} dish

Respond ONLY with this EXACT JSON format (no markdown, no extra text):
{{
  "recipe_name": "Recipe Name",
  "ingredients": "ingredient1 ingredient2 ingredient3",
  "cooking_time": 25,
  "meal_type": "{meal_type}",
  "cuisine": "{cuisine}",
  "instructions": "Step 1. Step 2. Step 3. etc",
  "reason": "Why this recipe is perfect for your ingredients and time"
}}"""
    
    try:
        # Get available model
        model_name = get_available_model()
        
        # Use Gemini API
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        if not response.text:
            return None
        
        # Parse JSON response
        response_text = response.text.strip()
        
        # Handle markdown code blocks
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        response_text = response_text.strip()
        result = json.loads(response_text)
        
        # Validate and return recipe
        if all(key in result for key in ["recipe_name", "ingredients", "cooking_time", "instructions"]):
            result["reason"] = result.get("reason", "Perfect match for your ingredients and time!")
            return result
        
        return None
    
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse Gemini response: {str(e)}")
    
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")


def generate_multiple_recipes(
    user_ingredients: List[str],
    meal_type: str,
    cuisine: str,
    cooking_time: int,
    num_recipes: int = 3
) -> Optional[List[Dict]]:
    """
    Generate multiple different recipes using Gemini AI.
    
    Args:
        user_ingredients: Normalized list of user ingredients
        meal_type: Selected meal type
        cuisine: Selected cuisine
        cooking_time: Available cooking time
        num_recipes: Number of recipes to generate (default 3)
    
    Returns:
        List of recipe dictionaries, or None on failure
    """
    
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables!")
    
    # Build prompt to generate multiple recipes at once
    prompt = f"""Generate {num_recipes} DIFFERENT {cuisine} {meal_type.lower()} recipes using these ingredients: {', '.join(user_ingredients)}.
Cooking time: {cooking_time} minutes maximum per recipe.

Requirements:
1. Generate {num_recipes} COMPLETELY DIFFERENT recipes
2. Each should use MOST of the given ingredients but in different ways
3. Each must fit within the time limit
4. Each should be a valid {cuisine} {meal_type} dish

Respond ONLY with this EXACT JSON format (no markdown, no extra text, just the array):
[
  {{
    "recipe_name": "Recipe 1 Name",
    "ingredients": "ingredient1 ingredient2 ingredient3",
    "cooking_time": 25,
    "meal_type": "{meal_type}",
    "cuisine": "{cuisine}",
    "instructions": "Step 1. Step 2. Step 3.",
    "reason": "Why this recipe works"
  }},
  {{
    "recipe_name": "Recipe 2 Name",
    "ingredients": "ingredient1 ingredient2 ingredient3",
    "cooking_time": 30,
    "meal_type": "{meal_type}",
    "cuisine": "{cuisine}",
    "instructions": "Step 1. Step 2. Step 3.",
    "reason": "Why this recipe works"
  }},
  {{
    "recipe_name": "Recipe 3 Name",
    "ingredients": "ingredient1 ingredient2 ingredient3",
    "cooking_time": 35,
    "meal_type": "{meal_type}",
    "cuisine": "{cuisine}",
    "instructions": "Step 1. Step 2. Step 3.",
    "reason": "Why this recipe works"
  }}
]"""
    
    try:
        # Get available model
        model_name = get_available_model()
        
        # Use Gemini API
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        if not response.text:
            return None
        
        # Parse JSON response with robust handling
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if "```" in response_text:
            parts = response_text.split("```")
            response_text = parts[1] if len(parts) > 1 else response_text
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        response_text = response_text.strip()
        
        # Find JSON array boundaries - extract only the JSON part
        start_idx = response_text.find("[")
        end_idx = response_text.rfind("]")
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx+1]
        else:
            json_str = response_text
        
        # Parse the JSON
        results = json.loads(json_str)
        
        # Validate results
        if isinstance(results, list) and len(results) > 0:
            recipes = []
            for result in results:
                if all(key in result for key in ["recipe_name", "ingredients", "cooking_time", "instructions"]):
                    result["reason"] = result.get("reason", "Perfect match for your ingredients and time!")
                    recipes.append(result)
            
            return recipes if recipes else None
        
        return None
    
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse Gemini response: {str(e)}")
    
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")


def validate_api_key() -> bool:
    """Check if Gemini API key is configured."""
    return bool(API_KEY)
