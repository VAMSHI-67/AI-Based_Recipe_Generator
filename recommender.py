import pandas as pd
from typing import List, Dict
from utils.preprocessing import normalize_ingredients


def calculate_ingredient_overlap(recipe_ingredients: str, user_ingredients: List[str]) -> float:
    """
    Calculate the percentage of recipe ingredients that match user ingredients.
    
    Args:
        recipe_ingredients: Comma-separated string of recipe ingredients
        user_ingredients: List of normalized user ingredients
    
    Returns:
        Overlap percentage (0-100)
    """
    recipe_ing_list = [ing.strip().lower() for ing in recipe_ingredients.split(',')]
    user_ing_set = set(user_ingredients)
    
    if len(recipe_ing_list) == 0:
        return 0
    
    matches = sum(1 for ing in recipe_ing_list if ing in user_ing_set)
    overlap = (matches / len(recipe_ing_list)) * 100
    
    return overlap


def filter_recipes(
    recipes_df: pd.DataFrame,
    user_ingredients: List[str],
    max_cooking_time: int,
    meal_type: str,
    cuisine: str,
    min_overlap: float = 0.6
) -> pd.DataFrame:
    """
    Rule-based filtering of recipes based on user criteria.
    
    Filters by:
    - Cooking time constraint
    - Meal type match
    - Cuisine match
    - Ingredient overlap >= 60%
    
    Args:
        recipes_df: DataFrame of all recipes
        user_ingredients: List of normalized user ingredients
        max_cooking_time: Maximum available cooking time
        meal_type: Desired meal type
        cuisine: Desired cuisine
        min_overlap: Minimum ingredient overlap percentage (0-1)
    
    Returns:
        Filtered DataFrame of matching recipes
    """
    
    # Create a copy to avoid modifying original
    filtered = recipes_df.copy()
    
    # Filter by cooking time
    filtered = filtered[filtered['cooking_time'] <= max_cooking_time]
    
    # Filter by meal type (case-insensitive)
    filtered = filtered[filtered['meal_type'].str.lower() == meal_type.lower()]
    
    # Filter by cuisine (case-insensitive)
    filtered = filtered[filtered['cuisine'].str.lower() == cuisine.lower()]
    
    # Calculate and filter by ingredient overlap
    filtered['ingredient_overlap'] = filtered['ingredients'].apply(
        lambda x: calculate_ingredient_overlap(x, user_ingredients)
    )
    
    # Filter by minimum overlap threshold (60%)
    filtered = filtered[filtered['ingredient_overlap'] >= (min_overlap * 100)]
    
    # Sort by ingredient overlap in descending order
    filtered = filtered.sort_values('ingredient_overlap', ascending=False)
    
    return filtered.reset_index(drop=True)


def get_top_candidates(
    recipes_df: pd.DataFrame,
    user_ingredients: List[str],
    top_n: int = 5
) -> List[Dict]:
    """
    Extract top N recipes as candidates for AI ranking.
    
    Args:
        recipes_df: Filtered DataFrame of recipes
        user_ingredients: List of normalized user ingredients
        top_n: Number of top candidates to return
    
    Returns:
        List of recipe dictionaries
    """
    
    # Get top recipes
    top_recipes = recipes_df.head(top_n)
    
    # Convert to list of dictionaries
    candidates = []
    for _, row in top_recipes.iterrows():
        candidate = {
            'recipe_name': row['recipe_name'],
            'ingredients': row['ingredients'],
            'cooking_time': row['cooking_time'],
            'meal_type': row['meal_type'],
            'cuisine': row['cuisine'],
            'instructions': row['instructions'],
            'ingredient_overlap': row.get('ingredient_overlap', 0)
        }
        candidates.append(candidate)
    
    return candidates


def score_recipe(
    recipe: Dict,
    user_ingredients: List[str],
    cooking_time_limit: int
) -> float:
    """
    Score a recipe based on multiple factors (for future enhancement).
    
    Args:
        recipe: Recipe dictionary
        user_ingredients: List of normalized user ingredients
        cooking_time_limit: Available cooking time
    
    Returns:
        Score between 0 and 100
    """
    
    # Ingredient match score (40% weight)
    ingredient_overlap = calculate_ingredient_overlap(
        recipe['ingredients'],
        user_ingredients
    )
    ingredient_score = min(ingredient_overlap, 100) * 0.4
    
    # Time efficiency score (30% weight)
    time_efficiency = (recipe['cooking_time'] / cooking_time_limit) * 100
    time_score = max(0, (100 - time_efficiency)) * 0.3
    
    # Base match score (30% weight)
    base_score = 30
    
    total_score = ingredient_score + time_score + base_score
    
    return min(total_score, 100)
