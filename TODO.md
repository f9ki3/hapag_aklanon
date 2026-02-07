# TODO - Recipe Schema Transformation

## Goal

Transform `recipe.json` from array format to UUID-keyed dictionary format with the specified schema.

## Steps Completed

- [x] 1. Create transform_recipe_json.py script to convert array to UUID-keyed dict
- [x] 2. Transform recipe.json to new schema structure
- [x] 3. Update upload_recipes.py to handle dictionary format
- [x] 4. Remove cooking_time and servings from form and API
- [x] 5. Add image upload option (URL or file upload with base64 conversion)
- [x] 6. Add recipes table with View/Edit/Delete functionality using offcanvas

## Notes

- Current format: Dictionary with UUID keys, each value is a recipe object
- Each recipe has: created_at, description, dish_name, image_url, ingredients, location, procedure, updated_at
- Form now supports: Image URL or File Upload with preview
- Recipes table with offcanvas for View and Edit actions
