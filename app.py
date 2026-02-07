"""
Hapag-Aklanon Recipe REST API
Flask-based REST API for managing recipe data stored in Firebase Realtime Database
Works with Firebase test rules (unauthenticated access)
Supports Cloudinary for image uploads
"""

from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import requests
import json
import os
import base64
from datetime import datetime, timezone, timedelta
import cloudinary
import cloudinary.uploader

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Firebase Configuration
FIREBASE_URL = os.environ.get(
    'FIREBASE_DATABASE_URL', 
    'https://hapag-aklanon-default-rtdb.asia-southeast1.firebasedatabase.app/'
)

# Cloudinary Configuration
cloudinary.config(
    cloud_name='dem5tr3uq',
    api_key='767752514795151',
    api_secret='fmgjyMAnXddYfUtN6GMki4BOAyc',
    secure=True
)

# ==================== HELPER FUNCTIONS ====================

def get_manila_timestamp():
    """Get current timestamp in Asia/Manila timezone (UTC+8)"""
    manila_tz = timezone(timedelta(hours=8))
    return datetime.now(manila_tz).strftime('%Y-%m-%dT%H:%M:%S+08:00')

def upload_image_to_cloudinary(image_data, folder='recipes'):
    """Upload base64 image to Cloudinary and return URL"""
    try:
        # Check if image_data is a base64 string starting with data:image
        if image_data and isinstance(image_data, str) and image_data.startswith('data:image'):
            result = cloudinary.uploader.upload(
                image_data,
                folder=folder,
                resource_type='image',
                transformation=[
                    {'width': 800, 'height': 600, 'crop': 'limit'},
                    {'quality': 'auto', 'fetch_format': 'auto'}
                ]
            )
            return result.get('secure_url', '')
        # Return as-is if it's already a URL
        elif image_data and isinstance(image_data, str):
            return image_data
        return ''
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        return image_data  # Return original if upload fails

def firebase_request(method, path='', data=None, params=None):
    """Make HTTP request to Firebase REST API"""
    url = f"{FIREBASE_URL}/{path}.json"
    
    try:
        if method == 'GET':
            response = requests.get(url, params=params)
        elif method == 'POST':
            response = requests.post(url, json=data, params=params)
        elif method == 'PUT':
            response = requests.put(url, json=data, params=params)
        elif method == 'PATCH':
            response = requests.patch(url, json=data, params=params)
        elif method == 'DELETE':
            response = requests.delete(url, params=params)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# ==================== API ROUTES ====================

@app.route('/')
def index():
    """API documentation"""
    return render_template('index.html')


@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    """Get all recipes with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        if page < 1: page = 1
        if limit < 1: limit = 10
        if limit > 100: limit = 100
        
        all_recipes = firebase_request('GET', 'recipes')
        
        # Handle Firebase response
        if all_recipes is None or all_recipes == 'null':
            return jsonify({
                "success": True, "data": [],
                "pagination": {"page": page, "limit": limit, "total_items": 0, "total_pages": 0}
            })
        
        if isinstance(all_recipes, dict):
            recipe_list = []
            for recipe_id, recipe_data in all_recipes.items():
                recipe_data['id'] = recipe_id
                recipe_list.append(recipe_data)
        else:
            recipe_list = []
        
        total_items = len(recipe_list)
        total_pages = (total_items + limit - 1) // limit
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_recipes = recipe_list[start_index:end_index]
        
        return jsonify({
            "success": True, "data": paginated_recipes,
            "pagination": {
                "page": page, "limit": limit, "total_items": total_items, "total_pages": total_pages,
                "has_next": page < total_pages, "has_prev": page > 1
            }
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/recipes/<recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    """Get a single recipe by ID"""
    try:
        recipe = firebase_request('GET', f'recipes/{recipe_id}')
        
        if recipe is None or recipe == 'null':
            return jsonify({"success": False, "error": "Recipe not found"}), 404
        
        if isinstance(recipe, str):
            return jsonify({"success": False, "error": recipe}), 500
        
        recipe['id'] = recipe_id
        return jsonify({"success": True, "data": recipe})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    """Create a new recipe"""
    try:
        data = request.get_json()
        
        if data is None:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400
        
        required_fields = ['location', 'dish_name', 'description', 'ingredients', 'procedure']
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            return jsonify({"success": False, "error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        if not isinstance(data.get('ingredients'), list):
            return jsonify({"success": False, "error": "ingredients must be an array"}), 400
        
        if not isinstance(data.get('procedure'), list):
            return jsonify({"success": False, "error": "procedure must be an array"}), 400
        
        # Handle image upload to Cloudinary
        image_url = data.get('image_url', '')
        if image_url:
            # Upload to Cloudinary if it's a base64 string
            uploaded_url = upload_image_to_cloudinary(image_url)
            if uploaded_url:
                image_url = uploaded_url
            else:
                # Use placeholder if upload fails and no valid URL
                image_url = f"https://placehold.co/600x400?text={data.get('dish_name', 'Recipe')}"
        else:
            # Generate placeholder image URL
            image_url = f"https://placehold.co/600x400?text={data.get('dish_name', 'Recipe')}"
        
        recipe_data = {
            'location': data['location'],
            'dish_name': data['dish_name'],
            'description': data['description'],
            'ingredients': data['ingredients'],
            'procedure': data['procedure'],
            'image_url': image_url
        }
        
        for field in ['category']:
            if field in data and data[field]:
                recipe_data[field] = data[field]
        
        # Add timestamps
        timestamp = get_manila_timestamp()
        recipe_data['created_at'] = data.get('created_at', timestamp)
        recipe_data['updated_at'] = timestamp
        
        # Firebase requires auth for POST, so we use PUT with a generated key
        import uuid
        recipe_key = str(uuid.uuid4())
        result = firebase_request('PUT', f'recipes/{recipe_key}', recipe_data)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({"success": False, "error": result['error']}), 500
        
        recipe_data['id'] = recipe_key
        
        return jsonify({
            "success": True, "message": "Recipe created successfully",
            "data": recipe_data
        }), 201
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/recipes/<recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    """Delete a recipe by ID"""
    try:
        # Check if recipe exists
        recipe = firebase_request('GET', f'recipes/{recipe_id}')
        if recipe is None or recipe == 'null':
            return jsonify({"success": False, "error": "Recipe not found"}), 404
        
        result = firebase_request('DELETE', f'recipes/{recipe_id}')
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({"success": False, "error": result['error']}), 500
        
        return jsonify({"success": True, "message": "Recipe deleted successfully", "deleted_id": recipe_id})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/recipes/search', methods=['GET'])
def search_recipes():
    """Search recipes by location or dish_name"""
    try:
        query = request.args.get('q', '', type=str)
        search_field = request.args.get('field', 'both', type=str).lower()
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({"success": False, "error": "Search query (q) is required"}), 400
        
        if page < 1: page = 1
        if limit < 1: limit = 10
        if limit > 100: limit = 100
        
        if search_field not in ['location', 'dish_name', 'both']:
            search_field = 'both'
        
        all_recipes = firebase_request('GET', 'recipes')
        
        if all_recipes is None or all_recipes == 'null':
            return jsonify({
                "success": True, "data": [],
                "pagination": {"page": page, "limit": limit, "total_items": 0, "total_pages": 0}
            })
        
        if isinstance(all_recipes, dict):
            recipe_list = []
            query_lower = query.lower()
            
            for recipe_id, recipe_data in all_recipes.items():
                recipe_data['id'] = recipe_id
                
                fields_to_search = []
                if search_field in ['location', 'both']:
                    fields_to_search.append('location')
                if search_field in ['dish_name', 'both']:
                    fields_to_search.append('dish_name')
                
                matches = False
                for field in fields_to_search:
                    if field in recipe_data:
                        if query_lower in str(recipe_data[field]).lower():
                            matches = True
                            break
                
                if matches:
                    recipe_list.append(recipe_data)
        else:
            recipe_list = []
        
        total_items = len(recipe_list)
        total_pages = (total_items + limit - 1) // limit
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_recipes = recipe_list[start_index:end_index]
        
        return jsonify({
            "success": True, "data": paginated_recipes,
            "search_query": query, "search_field": search_field,
            "pagination": {
                "page": page, "limit": limit, "total_items": total_items, "total_pages": total_pages,
                "has_next": page < total_pages, "has_prev": page > 1
            }
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/recipes/<recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    """Update an existing recipe"""
    try:
        data = request.get_json()
        
        if data is None:
            return jsonify({"success": False, "error": "No JSON data provided"}), 400
        
        # Check if recipe exists
        existing = firebase_request('GET', f'recipes/{recipe_id}')
        if existing is None or existing == 'null':
            return jsonify({"success": False, "error": "Recipe not found"}), 404
        
        if 'id' in data:
            del data['id']
        
        if 'ingredients' in data and not isinstance(data['ingredients'], list):
            return jsonify({"success": False, "error": "ingredients must be an array"}), 400
        
        if 'procedure' in data and not isinstance(data['procedure'], list):
            return jsonify({"success": False, "error": "procedure must be an array"}), 400
        
        # Handle image upload to Cloudinary if image_url is being updated
        if 'image_url' in data and data['image_url']:
            uploaded_url = upload_image_to_cloudinary(data['image_url'])
            if uploaded_url:
                data['image_url'] = uploaded_url
            else:
                del data['image_url']
        
        update_data = {}
        allowed_fields = ['location', 'dish_name', 'description', 'ingredients', 
                         'procedure', 'image_url', 'category']
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        # Always update the updated_at timestamp
        update_data['updated_at'] = get_manila_timestamp()
        
        if not update_data:
            return jsonify({"success": False, "error": "No valid fields to update"}), 400
        
        result = firebase_request('PATCH', f'recipes/{recipe_id}', update_data)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({"success": False, "error": result['error']}), 500
        
        updated_recipe = firebase_request('GET', f'recipes/{recipe_id}')
        updated_recipe['id'] = recipe_id
        
        return jsonify({"success": True, "message": "Recipe updated successfully", "data": updated_recipe})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/recipes/bulk', methods=['POST'])
def bulk_insert():
    """Insert multiple recipes at once"""
    try:
        data = request.get_json()
        
        if data is None or 'recipes' not in data:
            return jsonify({"success": False, "error": "No recipes data provided"}), 400
        
        recipes = data['recipes']
        
        if not isinstance(recipes, list):
            return jsonify({"success": False, "error": "recipes must be an array"}), 400
        
        if len(recipes) == 0:
            return jsonify({"success": False, "error": "recipes array is empty"}), 400
        
        valid_recipes = []
        errors = []
        
        for idx, recipe in enumerate(recipes):
            if not isinstance(recipe, dict):
                errors.append(f"Item {idx}: Not a valid object")
                continue
            
            missing = [f for f in ['location', 'dish_name', 'description', 'ingredients', 'procedure'] 
                      if f not in recipe]
            if missing:
                errors.append(f"Item {idx}: Missing fields: {', '.join(missing)}")
                continue
            
            if not isinstance(recipe.get('ingredients'), list):
                errors.append(f"Item {idx}: ingredients must be an array")
                continue
            
            if not isinstance(recipe.get('procedure'), list):
                errors.append(f"Item {idx}: procedure must be an array")
                continue
            
            valid_recipes.append(recipe)
        
        if not valid_recipes:
            return jsonify({"success": False, "error": "No valid recipes to insert", "validation_errors": errors}), 400
        
        import uuid
        inserted_ids = []
        
        for recipe in valid_recipes:
            recipe_key = str(uuid.uuid4())
            result = firebase_request('PUT', f'recipes/{recipe_key}', recipe)
            
            if isinstance(result, dict) and 'error' in result:
                errors.append(f"Failed to insert: {recipe.get('dish_name', 'Unknown')}")
            else:
                inserted_ids.append(recipe_key)
        
        return jsonify({
            "success": True, "message": f"Successfully inserted {len(inserted_ids)} recipes",
            "inserted_count": len(inserted_ids), "inserted_ids": inserted_ids,
            "errors": errors if errors else None
        }), 201
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Resource not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"success": False, "error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting Hapag-Aklanon Recipe API on port {port}")
    print(f"Firebase URL: {FIREBASE_URL}")
    
    app.run(host='0.0.0.0', port=port, debug=True)

