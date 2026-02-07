"""
Script to upload initial recipe data from recipe.json to Firebase
Uses Firebase REST API - works with test rules
Usage: python upload_recipes.py
"""

import json
import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

# Load environment variables
load_dotenv()

# ==================== HELPER FUNCTIONS ====================

def get_manila_timestamp():
    """Get current timestamp in Asia/Manila timezone (UTC+8)"""
    manila_tz = timezone(timedelta(hours=8))
    return datetime.now(manila_tz).strftime('%Y-%m-%dT%H:%M:%S+08:00')

# Firebase Configuration
FIREBASE_URL = os.environ.get(
    'FIREBASE_DATABASE_URL', 
    'https://hapag-aklanon-default-rtdb.asia-southeast1.firebasedatabase.app/'
)

def firebase_put(path='', data=None):
    """Make PUT request to Firebase"""
    url = f"{FIREBASE_URL}/{path}.json"
    try:
        response = requests.put(url, json=data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def firebase_get(path=''):
    """Make GET request to Firebase"""
    url = f"{FIREBASE_URL}/{path}.json"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def firebase_delete(path=''):
    """Make DELETE request to Firebase"""
    url = f"{FIREBASE_URL}/{path}.json"
    try:
        response = requests.delete(url)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

def upload_recipes():
    """Upload recipes from recipe.json to Firebase"""
    try:
        print(f"Firebase URL: {FIREBASE_URL}")
        print()
        
        # Read recipe.json - now in UUID-keyed dictionary format
        recipes_file = os.path.join(os.path.dirname(__file__), 'recipe.json')
        print(f"Reading recipes from {recipes_file}...")
        
        with open(recipes_file, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
        
        # Handle both formats: dictionary (new) and array (legacy)
        if isinstance(recipes, dict):
            print(f"Found {len(recipes)} recipes in UUID-keyed format...")
            recipe_items = list(recipes.items())
        elif isinstance(recipes, list):
            print(f"Found {len(recipes)} recipes in array format...")
            # Generate UUIDs for array format
            recipe_items = []
            for recipe in recipes:
                import uuid
                recipe_id = str(uuid.uuid4())
                recipe_items.append((recipe_id, recipe))
        else:
            print("Error: Unknown recipe format")
            return False
        
        print()
        
        # First, clear existing recipes (optional - comment out if you want to keep them)
        print("Clearing existing recipes...")
        firebase_delete('recipes')
        print("Done.")
        print()
        
        # Upload each recipe
        imported_count = 0
        for idx, (recipe_id, recipe) in enumerate(recipe_items, 1):
            # Ensure image_url is present
            if 'image_url' not in recipe:
                recipe['image_url'] = f"https://placehold.co/600x400?text={recipe.get('dish_name', 'Recipe')}"
                print(f"  Auto-generated image_url for: {recipe.get('dish_name', 'Unknown')}")
            
            result = firebase_put(f'recipes/{recipe_id}', recipe)
            
            if isinstance(result, dict) and 'error' in result:
                print(f"  ✗ Error uploading {recipe.get('dish_name', 'Unknown')}: {result['error']}")
            else:
                imported_count += 1
                print(f"  {idx}. Uploaded: {recipe.get('dish_name', 'Unknown')} ({recipe.get('location', 'Unknown')}) -> {recipe_id}")
        
        print()
        print(f"✓ Successfully imported {imported_count} recipes to Firebase!")
        print()
        
        # Verify
        all_recipes = firebase_get('recipes')
        if isinstance(all_recipes, dict):
            print(f"Total recipes in Firebase: {len(all_recipes)}")
        
        return True
        
    except FileNotFoundError:
        print("✗ Error: recipe.json file not found!")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON in recipe.json - {e}")
        return False
    except Exception as e:
        print(f"✗ Error uploading recipes: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Hapag-Aklanon Recipe Importer")
    print("=" * 60)
    print()
    upload_recipes()
    print()
    print("=" * 60)

