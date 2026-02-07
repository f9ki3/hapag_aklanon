# Hapag-Aklanon Recipe API Documentation

## Base URL

```
http://localhost:5000
```

## Endpoints

### 1. Get All Recipes (with pagination)

**Endpoint:** `GET /api/recipes`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number |
| limit | integer | 10 | Items per page (max: 100) |

**Example Request:**

```bash
curl "http://localhost:5000/api/recipes?page=1&limit=5"
```

**Example Response:**

```json
{
  "success": true,
  "data": [
    {
      "id": "-Nk123...",
      "location": "MAKATO",
      "dish_name": "Iniraran",
      "description": "Grilled pork or chicken...",
      "ingredients": ["1 kg pork...", "1/2 cup vinegar..."],
      "procedure": ["In a large bowl...", "Cover and marinate..."]
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 5,
    "total_items": 6,
    "total_pages": 2,
    "has_next": true,
    "has_prev": false
  }
}
```

---

### 2. Get Single Recipe

**Endpoint:** `GET /api/recipes/<recipe_id>`

**Example Request:**

```bash
curl "http://localhost:5000/api/recipes/-Nk123abc..."
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "id": "-Nk123abc...",
    "location": "MAKATO",
    "dish_name": "Iniraran",
    "description": "Grilled pork or chicken...",
    "ingredients": ["1 kg pork...", "1/2 cup vinegar..."],
    "procedure": ["In a large bowl...", "Cover and marinate..."]
  }
}
```

---

### 3. Create Recipe

**Endpoint:** `POST /api/recipes`

**Request Body (JSON):**

```json
{
  "location": "NEW_LOCATION",
  "dish_name": "New Dish Name",
  "description": "Description of the dish",
  "ingredients": ["ingredient 1", "ingredient 2", "ingredient 3"],
  "procedure": ["Step 1", "Step 2", "Step 3"],
  "image_url": "https://example.com/image.jpg",
  "cooking_time": 60,
  "servings": 4,
  "category": "Main Course"
}
```

**Example Request:**

```bash
curl -X POST "http://localhost:5000/api/recipes" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "KALIBO",
    "dish_name": "Kinilaw",
    "description": "Fresh fish ceviche",
    "ingredients": ["1 kg fresh tuna", "1 cup vinegar", "Ginger", "Onion"],
    "procedure": ["Clean the fish", "Slice into cubes", "Mix with vinegar"]
  }'
```

**Example Response:**

```json
{
  "success": true,
  "message": "Recipe created successfully",
  "data": {
    "id": "-Nk456def...",
    "location": "KALIBO",
    "dish_name": "Kinilaw",
    "description": "Fresh fish ceviche",
    "ingredients": ["1 kg fresh tuna", "1 cup vinegar", "Ginger", "Onion"],
    "procedure": ["Clean the fish", "Slice into cubes", "Mix with vinegar"]
  }
}
```

---

### 4. Delete Recipe

**Endpoint:** `DELETE /api/recipes/<recipe_id>`

**Example Request:**

```bash
curl -X DELETE "http://localhost:5000/api/recipes/-Nk123abc..."
```

**Example Response:**

```json
{
  "success": true,
  "message": "Recipe deleted successfully",
  "deleted_id": "-Nk123abc..."
}
```

---

### 5. Search Recipes

**Endpoint:** `GET /api/recipes/search`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | Search query |
| field | string | No | Search field: `location`, `dish_name`, or `both` (default: `both`) |
| page | integer | No | Page number (default: 1) |
| limit | integer | No | Items per page (default: 10) |

**Example Requests:**

```bash
# Search by location
curl "http://localhost:5000/api/recipes/search?q=MAKATO&field=location"

# Search by dish name
curl "http://localhost:5000/api/recipes/search?q=Iniraran&field=dish_name"

# Search both fields
curl "http://localhost:5000/api/recipes/search?q=chicken"
```

---

### 6. Update Recipe

**Endpoint:** `PUT /api/recipes/<recipe_id>`

**Request Body (JSON) - Partial updates allowed:**

```json
{
  "dish_name": "Updated Dish Name",
  "description": "Updated description"
}
```

**Example Request:**

```bash
curl -X PUT "http://localhost:5000/api/recipes/-Nk123abc..." \
  -H "Content-Type: application/json" \
  -d '{"dish_name": "Updated Iniraran"}'
```

---

### 7. Bulk Insert Recipes

**Endpoint:** `POST /api/recipes/bulk`

**Request Body (JSON):**

```json
{
  "recipes": [
    {
      "location": "LOCATION_1",
      "dish_name": "Dish 1",
      "description": "Description 1",
      "ingredients": ["ing1", "ing2"],
      "procedure": ["step1", "step2"]
    },
    {
      "location": "LOCATION_2",
      "dish_name": "Dish 2",
      "description": "Description 2",
      "ingredients": ["ing3", "ing4"],
      "procedure": ["step3", "step4"]
    }
  ]
}
```

---

## Error Responses

**400 Bad Request:**

```json
{
  "success": false,
  "error": "Error message describing the issue"
}
```

**404 Not Found:**

```json
{
  "success": false,
  "error": "Recipe not found"
}
```

**500 Internal Server Error:**

```json
{
  "success": false,
  "error": "Internal server error message"
}
```

---

## Recipe Structure

```json
{
  "id": "string (auto-generated)",
  "location": "string (required)",
  "dish_name": "string (required)",
  "description": "string (required)",
  "ingredients": ["string", ...] (required),
  "procedure": ["string", ...] (required),
  "image_url": "string (optional)",
  "cooking_time": integer (optional, in minutes)",
  "servings": integer (optional)",
  "category": "string (optional)"
}
```

---

## Running the Server

### Development

```bash
python app.py
```

### With Custom Port

```bash
PORT=8080 python app.py
```

### Debug Mode

```bash
DEBUG=True python app.py
```

---

## Firebase Setup

1. **Option 1: Environment Variables**
   Copy `.env.example` to `.env` and fill in your Firebase credentials

2. **Option 2: JSON File**
   Copy `firebase-credentials.example.json` to `firebase-credentials.json` and fill in your credentials

---

## Uploading Initial Data

To upload the recipes from `recipe.json` to Firebase:

```bash
python upload_recipes.py
```
