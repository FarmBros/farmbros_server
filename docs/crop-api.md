# Crop API Documentation

## Overview

The Crop API provides endpoints to manage agricultural crop definitions in the FarmBros system. Crops are the foundational data for tracking planting activities, with detailed information about growth characteristics, nutrient needs, and expected yields.

**Base URL:** `/crops`

## Authentication

- **Admin endpoints** require admin role authentication
- **User endpoints** require standard user authentication
- All endpoints require a valid JWT token in the Authorization header: `Bearer <token>`

## Data Model

### Crop Object

```json
{
  "id": 1,
  "uuid": "8d99a668-1863-4f4b-8025-b50e66c48ff5",
  "common_name": "Tomato",
  "genus": "Solanum",
  "species": "lycopersicum",
  "scientific_name": "Solanum lycopersicum",
  "crop_group": "vegetable",
  "lifecycle": "annual",
  "germination_days": 7,
  "days_to_transplant": 21,
  "days_to_maturity": 80,
  "nitrogen_needs": 150.5,
  "phosphorus_needs": 80.0,
  "potassium_needs": 200.0,
  "water_coefficient": 0.85,
  "yield_per_plant": 5.5,
  "yield_per_area": 12.0,
  "planting_methods": "direct_seed, transplant",
  "planting_spacing_m": 0.5,
  "row_spacing_m": 1.0,
  "seedling_type": "transplant",
  "notes": "Requires staking and regular pruning",
  "created_at": "2024-11-15T10:30:00",
  "updated_at": "2024-11-15T10:30:00"
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Internal database ID (read-only) |
| `uuid` | String | External unique identifier (UUID format) |
| `common_name` | String | Common name of the crop (required) |
| `genus` | String | Taxonomic genus |
| `species` | String | Taxonomic species |
| `scientific_name` | String | Full scientific name (auto-generated from genus + species) |
| `crop_group` | Enum | Crop classification (see Enums section) |
| `lifecycle` | Enum | Plant lifecycle type (see Enums section) |
| `germination_days` | Integer | Days from seeding to germination |
| `days_to_transplant` | Integer | Days from germination to transplant readiness |
| `days_to_maturity` | Integer | Total days from planting to harvest |
| `nitrogen_needs` | Float | Nitrogen requirements (mg per plant or per m²) |
| `phosphorus_needs` | Float | Phosphorus requirements (mg per plant or per m²) |
| `potassium_needs` | Float | Potassium requirements (mg per plant or per m²) |
| `water_coefficient` | Float | Relative water needs (0-1 scale) |
| `yield_per_plant` | Float | Expected yield per plant (kg) |
| `yield_per_area` | Float | Expected yield per square meter (kg) |
| `planting_methods` | String | Comma-separated list of planting methods |
| `planting_spacing_m` | Float | Spacing between plants (meters) |
| `row_spacing_m` | Float | Spacing between rows (meters) |
| `seedling_type` | Enum | Starting method (see Enums section) |
| `notes` | Text | Additional information or notes |
| `created_at` | DateTime | Creation timestamp (ISO 8601) |
| `updated_at` | DateTime | Last update timestamp (ISO 8601) |

### Enums

#### CropGroup
- `fruit` - Fruit crops
- `vegetable` - Vegetable crops
- `cereal` - Cereal/grain crops
- `legume` - Leguminous crops
- `root` - Root vegetables
- `tuber` - Tuber crops
- `leafy_green` - Leafy greens
- `herb` - Herbs
- `flower` - Flowering crops
- `other` - Other crop types

#### Lifecycle
- `annual` - Annual plants (one growing season)
- `perennial` - Perennial plants (multiple seasons)
- `biennial` - Biennial plants (two seasons)

#### SeedlingType
- `direct_seed` - Direct seeded only
- `transplant` - Transplanted only
- `both` - Can be direct seeded or transplanted

## API Endpoints

### 1. Create Crop

Create a new crop definition.

**Endpoint:** `POST /crops/create`
**Auth Required:** Admin only
**Request Body:**

```json
{
  "common_name": "Tomato",
  "genus": "Solanum",
  "species": "lycopersicum",
  "crop_group": "vegetable",
  "lifecycle": "annual",
  "germination_days": 7,
  "days_to_transplant": 21,
  "days_to_maturity": 80,
  "nitrogen_needs": 150.5,
  "phosphorus_needs": 80.0,
  "potassium_needs": 200.0,
  "water_coefficient": 0.85,
  "yield_per_plant": 5.5,
  "yield_per_area": 12.0,
  "planting_methods": "direct_seed, transplant",
  "planting_spacing_m": 0.5,
  "row_spacing_m": 1.0,
  "seedling_type": "transplant",
  "notes": "Requires staking and regular pruning"
}
```

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "8d99a668-1863-4f4b-8025-b50e66c48ff5",
    "common_name": "Tomato",
    ...
  },
  "error": null
}
```

**Error Response:**

```json
{
  "status": "error",
  "data": null,
  "error": "common_name is required"
}
```

---

### 2. Get Crop

Retrieve a single crop by UUID.

**Endpoint:** `POST /crops/get`
**Auth Required:** Yes (Any authenticated user)
**Request Body:**

```json
{
  "crop_id": "8d99a668-1863-4f4b-8025-b50e66c48ff5"
}
```

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "8d99a668-1863-4f4b-8025-b50e66c48ff5",
    "common_name": "Tomato",
    ...
  },
  "error": null
}
```

**Error Response:**

```json
{
  "status": "error",
  "data": null,
  "error": "Crop with uuid 8d99a668-1863-4f4b-8025-b50e66c48ff5 not found"
}
```

---

### 3. Get All Crops

Retrieve all crops with optional filtering and pagination.

**Endpoint:** `POST /crops/get_all`
**Auth Required:** Yes (Any authenticated user)
**Request Body:**

```json
{
  "skip": 0,
  "limit": 100,
  "crop_group": "vegetable",
  "lifecycle": "annual"
}
```

**Parameters:**
- `skip` (optional, default: 0) - Number of records to skip for pagination
- `limit` (optional, default: 100) - Maximum number of records to return
- `crop_group` (optional) - Filter by crop group enum value
- `lifecycle` (optional) - Filter by lifecycle enum value

**Success Response:**

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "uuid": "8d99a668-1863-4f4b-8025-b50e66c48ff5",
      "common_name": "Tomato",
      ...
    },
    {
      "id": 2,
      "uuid": "9fdec237-2122-4ae9-af10-de5abe7bdc47",
      "common_name": "Bell Pepper",
      ...
    }
  ],
  "error": null
}
```

---

### 4. Update Crop

Update an existing crop definition.

**Endpoint:** `POST /crops/update`
**Auth Required:** Admin only
**Request Body:**

```json
{
  "crop_id": "8d99a668-1863-4f4b-8025-b50e66c48ff5",
  "days_to_maturity": 85,
  "yield_per_plant": 6.0,
  "notes": "Updated yield estimate based on recent data"
}
```

**Note:** Only include fields you want to update. The `crop_id` field is required to identify the crop.

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "8d99a668-1863-4f4b-8025-b50e66c48ff5",
    "common_name": "Tomato",
    "days_to_maturity": 85,
    "yield_per_plant": 6.0,
    ...
  },
  "error": null
}
```

---

### 5. Delete Crop

Delete a crop definition.

**Endpoint:** `POST /crops/delete`
**Auth Required:** Admin only
**Request Body:**

```json
{
  "crop_id": "8d99a668-1863-4f4b-8025-b50e66c48ff5"
}
```

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "message": "Crop 8d99a668-1863-4f4b-8025-b50e66c48ff5 deleted successfully"
  },
  "error": null
}
```

**Error Response:**

```json
{
  "status": "error",
  "data": null,
  "error": "Cannot delete crop: it is referenced by planted crops"
}
```

---

### 6. Search Crops

Search for crops by common name, genus, or species.

**Endpoint:** `POST /crops/search`
**Auth Required:** Yes (Any authenticated user)
**Request Body:**

```json
{
  "search_term": "tomato",
  "skip": 0,
  "limit": 50
}
```

**Parameters:**
- `search_term` (required) - Text to search for in common_name, genus, or species
- `skip` (optional, default: 0) - Number of records to skip
- `limit` (optional, default: 50) - Maximum number of records to return

**Success Response:**

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "uuid": "8d99a668-1863-4f4b-8025-b50e66c48ff5",
      "common_name": "Tomato",
      "genus": "Solanum",
      "species": "lycopersicum",
      ...
    },
    {
      "id": 5,
      "uuid": "7abc1234-5678-90ab-cdef-1234567890ab",
      "common_name": "Cherry Tomato",
      "genus": "Solanum",
      "species": "lycopersicum var. cerasiforme",
      ...
    }
  ],
  "error": null
}
```

---

### 7. Count Crops

Get the total count of crops with optional filtering.

**Endpoint:** `POST /crops/count`
**Auth Required:** Admin only
**Request Body:**

```json
{
  "crop_group": "vegetable",
  "lifecycle": "annual"
}
```

**Parameters:**
- `crop_group` (optional) - Filter by crop group
- `lifecycle` (optional) - Filter by lifecycle

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "count": 42
  },
  "error": null
}
```

---

### 8. Get Crop Statistics

Get statistical information about crops in the database.

**Endpoint:** `POST /crops/statistics`
**Auth Required:** Admin only
**Request Body:** `{}` (empty object)

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "total_crops": 150,
    "by_crop_group": [
      {"crop_group": "vegetable", "count": 60},
      {"crop_group": "fruit", "count": 40},
      {"crop_group": "cereal", "count": 20}
    ],
    "by_lifecycle": [
      {"lifecycle": "annual", "count": 100},
      {"lifecycle": "perennial", "count": 40},
      {"lifecycle": "biennial", "count": 10}
    ],
    "by_seedling_type": [
      {"seedling_type": "transplant", "count": 70},
      {"seedling_type": "direct_seed", "count": 50},
      {"seedling_type": "both", "count": 30}
    ]
  },
  "error": null
}
```

---

### 9. Import Crops from Dataset

Import crops from a JSON dataset file.

**Endpoint:** `POST /crops/import_dataset`
**Auth Required:** Admin only
**Request Body:**

```json
{
  "file_path": "assets/cropV2.json",
  "skip_existing": true
}
```

**Parameters:**
- `file_path` (optional, default: "assets/cropV2.json") - Path to the JSON file
- `skip_existing` (optional, default: true) - Skip crops that already exist (by common_name)

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "imported": 45,
    "skipped": 5,
    "total_in_file": 50
  },
  "error": null
}
```

---

## Error Handling

All endpoints return responses in the following format:

**Success:**
```json
{
  "status": "success",
  "data": { ... },
  "error": null
}
```

**Error:**
```json
{
  "status": "error",
  "data": null,
  "error": "Error message describing what went wrong"
}
```

### Common Error Messages

- `"common_name is required"` - Missing required field
- `"Crop with uuid {uuid} not found"` - Crop doesn't exist
- `"Invalid crop_group value"` - Invalid enum value
- `"search_term is required"` - Missing required search parameter
- `"Cannot delete crop: it is referenced by planted crops"` - Crop is in use

### HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Missing required parameters
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - User doesn't have required permissions (admin only endpoints)
- `500 Internal Server Error` - Server-side error

---

## Usage Examples

### Example 1: List All Vegetable Crops

```javascript
const response = await fetch('/crops/get_all', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    crop_group: 'vegetable',
    limit: 100
  })
});

const result = await response.json();
if (result.status === 'success') {
  console.log('Vegetables:', result.data);
}
```

### Example 2: Search for a Crop

```javascript
const response = await fetch('/crops/search', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    search_term: 'tomato',
    limit: 10
  })
});

const result = await response.json();
if (result.status === 'success') {
  console.log('Found crops:', result.data);
}
```

### Example 3: Create a New Crop (Admin)

```javascript
const response = await fetch('/crops/create', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ADMIN_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    common_name: 'Cucumber',
    genus: 'Cucumis',
    species: 'sativus',
    crop_group: 'vegetable',
    lifecycle: 'annual',
    days_to_maturity: 60,
    yield_per_plant: 3.5,
    seedling_type: 'both'
  })
});

const result = await response.json();
if (result.status === 'success') {
  console.log('Created crop:', result.data.uuid);
}
```

---

## Notes for Frontend Development

1. **Use UUIDs for References:** Always use the `uuid` field when referencing crops in other API calls (e.g., when creating planted crops)

2. **Enum Validation:** Validate enum values on the frontend before submission to provide better UX

3. **Pagination:** Implement pagination using `skip` and `limit` parameters for better performance with large datasets

4. **Search Debouncing:** Implement debouncing on search inputs to reduce API calls

5. **Admin Features:** Conditionally show create/update/delete/import features only to admin users

6. **Caching:** Crop data changes infrequently, consider implementing client-side caching for better performance
