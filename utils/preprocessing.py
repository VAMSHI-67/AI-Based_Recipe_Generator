import re
from typing import List


# Common ingredient aliases for normalization
INGREDIENT_ALIASES = {
    'tomato': ['tomatoes', 'tomatoe', 'tamatar'],
    'onion': ['onions', 'pyaz'],
    'garlic': ['garlics', 'lahsun'],
    'ginger': ['gingers', 'adrak'],
    'chicken': ['chickens', 'murgi', 'murgh'],
    'rice': ['rices', 'basmati', 'jasmine'],
    'oil': ['oils', 'ghee', 'butter'],
    'salt': ['salts', 'namak'],
    'pepper': ['peppers', 'black pepper', 'kali mirch'],
    'cumin': ['cumins', 'jeera'],
    'coriander': ['cilantro', 'dhania'],
    'turmeric': ['haldi'],
    'chili': ['chilies', 'red chili', 'lal mirch'],
    'milk': ['milks', 'doodh'],
    'yogurt': ['yoghurt', 'curd', 'dahi'],
    'flour': ['flours', 'maida'],
    'sugar': ['sugars', 'cheeni'],
    'water': ['waters'],
    'lemon': ['lemons', 'lime', 'nimbu'],
    'potato': ['potatoes', 'aloo'],
    'carrot': ['carrots', 'gajar'],
    'spinach': ['spinaches', 'palak'],
    'green beans': ['beans', 'string beans', 'lobiya'],
    'bell pepper': ['capsicum', 'simla mirch'],
    'mushroom': ['mushrooms', 'khumbh'],
    'peas': ['green peas', 'matar'],
    'paneer': ['cottage cheese', 'indian cheese'],
    'lentils': ['dal', 'daal', 'lens'],
    'chickpeas': ['chana', 'garbanzo'],
}


def normalize_ingredient(ingredient: str) -> str:
    """
    Normalize ingredient name by:
    - Converting to lowercase
    - Removing extra whitespace
    - Removing special characters
    - Replacing aliases with canonical form
    
    Args:
        ingredient: Raw ingredient string
    
    Returns:
        Normalized ingredient string
    """
    
    # Convert to lowercase
    normalized = ingredient.lower().strip()
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Remove special characters (keep alphanumeric and spaces)
    normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
    
    # Check if ingredient matches any alias
    for canonical, aliases in INGREDIENT_ALIASES.items():
        if normalized == canonical:
            return canonical
        for alias in aliases:
            if normalized == alias.lower():
                return canonical
    
    return normalized


def normalize_ingredients(ingredients_text: str) -> List[str]:
    """
    Normalize a comma-separated string of ingredients.
    
    Args:
        ingredients_text: Comma or newline separated ingredient string
    
    Returns:
        List of normalized ingredient names
    """
    
    # Split by comma or newline
    raw_ingredients = re.split(r'[,\n]', ingredients_text)
    
    # Normalize each ingredient
    normalized = [
        normalize_ingredient(ing)
        for ing in raw_ingredients
        if ing.strip()
    ]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_ingredients = []
    for ing in normalized:
        if ing and ing not in seen:
            unique_ingredients.append(ing)
            seen.add(ing)
    
    return unique_ingredients


def extract_keywords(text: str) -> List[str]:
    """
    Extract keywords from text (useful for recipe search).
    
    Args:
        text: Input text
    
    Returns:
        List of keywords
    """
    
    # Remove special characters and split
    words = re.findall(r'\b[a-z]+\b', text.lower())
    
    # Remove common stop words
    stop_words = {
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'be', 'been', 'being'
    }
    
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    return list(set(keywords))
