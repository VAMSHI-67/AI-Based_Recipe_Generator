from urllib.parse import quote


def generate_youtube_search_url(recipe_name: str, cuisine: str) -> str:
    """
    Generate a YouTube search URL for a recipe without using YouTube API.
    
    Args:
        recipe_name: Name of the recipe
        cuisine: Cuisine type
    
    Returns:
        YouTube search URL
    """
    
    # Build search query
    search_query = f"{recipe_name} {cuisine} recipe"
    
    # URL encode the query
    encoded_query = quote(search_query)
    
    # Construct YouTube search URL
    youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
    
    return youtube_url


def generate_youtube_playlist_url(cuisine: str) -> str:
    """
    Generate a YouTube search URL for cuisine-based recipes.
    
    Args:
        cuisine: Cuisine type
    
    Returns:
        YouTube search URL for cuisine
    """
    
    search_query = f"{cuisine} recipes"
    encoded_query = quote(search_query)
    
    return f"https://www.youtube.com/results?search_query={encoded_query}"
