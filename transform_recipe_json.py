"""
Transform recipe.json from array format to UUID-keyed dictionary format.
Usage: python transform_recipe_json.py
"""

import json
import uuid
import os
from datetime import datetime, timezone, timedelta

def get_manila_timestamp():
    """Get current timestamp in Asia/Manila timezone (UTC+8)"""
    manila_tz = timezone(timedelta(hours=8))
    return datetime.now(manila_tz).strftime('%Y-%m-%dT%H:%M:%S+08:00')

def transform_recipes():
    """Transform recipe array to UUID-keyed dictionary"""
    
    # Read the current recipe.json
    input_file = os.path.join(os.path.dirname(__file__), 'recipe.json')
    
    print(f"Reading recipes from {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    print(f"Found {len(recipes)} recipes to transform...")
    print()
    
    # Transform to UUID-keyed dictionary
    transformed = {}
    
    for idx, recipe in enumerate(recipes, 1):
        # Generate a consistent UUID for each recipe
        # For demonstration, we'll generate new UUIDs
        # In production, you might want to keep existing IDs
        recipe_id = str(uuid.uuid4())
        
        # Ensure required fields
        transformed_recipe = {
            "created_at": recipe.get('created_at', get_manila_timestamp()),
            "description": recipe.get('description', ''),
            "dish_name": recipe.get('dish_name', ''),
            "image_url": recipe.get('image_url', f"https://placehold.co/600x400?text={recipe.get('dish_name', 'Recipe')}"),
            "ingredients": recipe.get('ingredients', []),
            "location": recipe.get('location', ''),
            "procedure": recipe.get('procedure', []),
            "updated_at": recipe.get('updated_at', get_manila_timestamp())
        }
        
        transformed[recipe_id] = transformed_recipe
        print(f"  {idx}. {transformed_recipe['dish_name']} ({transformed_recipe['location']}) -> {recipe_id}")
    
    print()
    print(f"Transformed {len(transformed)} recipes to UUID-keyed format...")
    print()
    
    # Write to a new file for backup
    output_file = os.path.join(os.path.dirname(__file__), 'recipe_transformed.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(transformed, f, indent=2, ensure_ascii=False)
    
    print(f"Backup written to {output_file}")
    print()
    
    # Update the original file
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(transformed, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Updated {input_file} with new UUID-keyed format")
    print()
    
    return transformed

if __name__ == '__main__':
    print("=" * 60)
    print("Recipe JSON Transformer")
    print("Transforming array format to UUID-keyed dictionary format")
    print("=" * 60)
    print()
    
    transform_recipes()
    
    print()
    print("=" * 60)
    print("Transformation complete!")
    print("=" * 60)

