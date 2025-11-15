# Planted Crop API Documentation

## Overview

The Planted Crop API manages instances of crops that users have planted in their plots. This tracks when and where crops are planted, planting methods, expected yields, and harvest information. Each planted crop is tied to a specific user, plot, and crop definition.

**Base URL:** `/planted_crops`

## Authentication

- All endpoints require user authentication
- Users can only access their own planted crop records
- JWT token required in Authorization header: `Bearer <token>`

## Data Model

### PlantedCrop Object

```json
{
  "id": 1,
  "uuid": "abc123de-4567-89fg-hijk-lmnopqrstuv0",
  "crop_id": 15,
  "plot_id": 8,
  "user_id": 3,
  "planting_method": "transplant",
  "planting_spacing": 0.5,
  "germination_date": "2024-03-15T00:00:00",
  "transplant_date": "2024-04-05T00:00:00",
  "seedling_age": 21,
  "harvest_date": "2024-06-15T00:00:00",
  "number_of_crops": 24,
  "estimated_yield": 132.0,
  "notes": "Cherry tomatoes in greenhouse plot, started indoors",
  "created_at": "2024-03-10T10:30:00",
  "updated_at": "2024-03-10T10:30:00"
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Internal database ID (read-only) |
| `uuid` | String | External unique identifier (UUID format) |
| `crop_id` | Integer | Internal crop reference (read-only) |
| `plot_id` | Integer | Internal plot reference (read-only) |
| `user_id` | Integer | Internal user reference (read-only) |
| `planting_method` | String | How the crop was planted (e.g., "direct_seed", "transplant") |
| `planting_spacing` | Float | Spacing between plants in meters |
| `germination_date` | DateTime | Date when seeds germinated (ISO 8601) |
| `transplant_date` | DateTime | Date when seedlings were transplanted (ISO 8601) |
| `seedling_age` | Integer | Age of seedlings in days at transplant time |
| `harvest_date` | DateTime | Expected or actual harvest date (ISO 8601) |
| `number_of_crops` | Integer | Number of individual plants |
| `estimated_yield` | Float | Expected total yield in kilograms |
| `notes` | Text | Additional information or observations |
| `created_at` | DateTime | Record creation timestamp (ISO 8601) |
| `updated_at` | DateTime | Last update timestamp (ISO 8601) |

### PlantedCrop with Details Object

When using the `/get_with_details` endpoint, you'll also receive related crop, plot, and user information:

```json
{
  "id": 1,
  "uuid": "abc123de-4567-89fg-hijk-lmnopqrstuv0",
  ...
  "crop": {
    "uuid": "8d99a668-1863-4f4b-8025-b50e66c48ff5",
    "common_name": "Tomato",
    "scientific_name": "Solanum lycopersicum",
    "crop_group": "vegetable",
    ...
  },
  "plot": {
    "uuid": "9edec237-2122-4ae9-af10-de5abe7bdc47",
    "name": "Greenhouse A",
    "plot_type": "green-house",
    "area_sqm": 50.0,
    ...
  },
  "user": {
    "id": 3,
    "username": "farmer_john",
    "email": "john@example.com"
  }
}
```

---

## Important: UUID Convention

**All request body keys use the `_id` suffix, but values are always UUIDs (not integer IDs).**

Example:
```json
{
  "crop_id": "8d99a668-1863-4f4b-8025-b50e66c48ff5",  // Key ends with _id, value is UUID
  "plot_id": "9edec237-2122-4ae9-af10-de5abe7bdc47",  // Key ends with _id, value is UUID
  "planted_crop_id": "abc123de-4567-89fg-hijk-lmnopqrstuv0"  // Key ends with _id, value is UUID
}
```

---

## API Endpoints

### 1. Create Planted Crop

Create a new planted crop entry.

**Endpoint:** `POST /planted_crops/create`
**Auth Required:** Yes
**Request Body:**

```json
{
  "crop_id": "8d99a668-1863-4f4b-8025-b50e66c48ff5",
  "plot_id": "9edec237-2122-4ae9-af10-de5abe7bdc47",
  "planting_method": "transplant",
  "planting_spacing": 0.5,
  "germination_date": "2024-03-15T00:00:00Z",
  "transplant_date": "2024-04-05T00:00:00Z",
  "seedling_age": 21,
  "harvest_date": "2024-06-15T00:00:00Z",
  "number_of_crops": 24,
  "estimated_yield": 132.0,
  "notes": "Cherry tomatoes in greenhouse plot"
}
```

**Required Fields:**
- `crop_id` - UUID of the crop being planted
- `plot_id` - UUID of the plot where it's being planted

**Optional Fields:**
- All other fields are optional

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "abc123de-4567-89fg-hijk-lmnopqrstuv0",
    "crop_id": 15,
    "plot_id": 8,
    "user_id": 3,
    ...
  },
  "error": null
}
```

**Error Responses:**

```json
{
  "status": "error",
  "data": null,
  "error": "crop_id and plot_id are required"
}
```

```json
{
  "status": "error",
  "data": null,
  "error": "Crop with uuid 8d99a668-1863-4f4b-8025-b50e66c48ff5 not found"
}
```

```json
{
  "status": "error",
  "data": null,
  "error": "Cannot plant a crop in a barn plot type"
}
```

**Business Rules:**
- Crops can only be planted in the following plot types:
  - `field`
  - `pasture`
  - `natural-area`
  - `green-house`
- Attempting to plant in other plot types (barn, chicken-pen, cow-shed, fish-pond, residence, water-source) will return an error

---

### 2. Get Planted Crop

Retrieve a single planted crop by UUID.

**Endpoint:** `POST /planted_crops/get`
**Auth Required:** Yes
**Request Body:**

```json
{
  "planted_crop_id": "abc123de-4567-89fg-hijk-lmnopqrstuv0"
}
```

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "abc123de-4567-89fg-hijk-lmnopqrstuv0",
    "crop_id": 15,
    "plot_id": 8,
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
  "error": "Planted crop with uuid abc123de-4567-89fg-hijk-lmnopqrstuv0 not found or access denied"
}
```

**Note:** Users can only access their own planted crops. Attempting to access another user's planted crop will return the same "not found or access denied" error.

---

### 3. Get All Planted Crops

Retrieve all planted crops for the authenticated user with optional filtering and pagination.

**Endpoint:** `POST /planted_crops/get_all`
**Auth Required:** Yes
**Request Body:**

```json
{
  "skip": 0,
  "limit": 100,
  "plot_id": "9edec237-2122-4ae9-af10-de5abe7bdc47",
  "crop_id": "8d99a668-1863-4f4b-8025-b50e66c48ff5"
}
```

**Parameters:**
- `skip` (optional, default: 0) - Number of records to skip for pagination
- `limit` (optional, default: 100) - Maximum number of records to return
- `plot_id` (optional) - Filter by plot UUID
- `crop_id` (optional) - Filter by crop UUID

**Success Response:**

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "uuid": "abc123de-4567-89fg-hijk-lmnopqrstuv0",
      "crop_id": 15,
      "plot_id": 8,
      ...
    },
    {
      "id": 2,
      "uuid": "def456gh-7890-12ij-klmn-opqrstuvwxy1",
      "crop_id": 22,
      "plot_id": 8,
      ...
    }
  ],
  "error": null
}
```

**Note:** Only returns planted crops belonging to the authenticated user.

---

### 4. Get Planted Crops with Details

Retrieve planted crops with full details about the crop, plot, and user.

**Endpoint:** `POST /planted_crops/get_with_details`
**Auth Required:** Yes
**Request Body:**

```json
{
  "skip": 0,
  "limit": 100,
  "plot_id": "9edec237-2122-4ae9-af10-de5abe7bdc47"
}
```

**Parameters:**
- `skip` (optional, default: 0) - Number of records to skip for pagination
- `limit` (optional, default: 100) - Maximum number of records to return
- `plot_id` (optional) - Filter by plot UUID

**Success Response:**

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "uuid": "abc123de-4567-89fg-hijk-lmnopqrstuv0",
      "crop_id": 15,
      "plot_id": 8,
      "user_id": 3,
      "planting_method": "transplant",
      "number_of_crops": 24,
      "estimated_yield": 132.0,
      ...
      "crop": {
        "uuid": "8d99a668-1863-4f4b-8025-b50e66c48ff5",
        "common_name": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "crop_group": "vegetable",
        "days_to_maturity": 80,
        "yield_per_plant": 5.5,
        ...
      },
      "plot": {
        "uuid": "9edec237-2122-4ae9-af10-de5abe7bdc47",
        "name": "Greenhouse A",
        "plot_type": "green-house",
        "area_sqm": 50.0,
        ...
      },
      "user": {
        "id": 3,
        "username": "farmer_john",
        "email": "john@example.com"
      }
    }
  ],
  "error": null
}
```

**Use Case:** This endpoint is ideal for displaying planted crop lists with full context (crop name, plot name, etc.) without making additional API calls.

---

### 5. Update Planted Crop

Update an existing planted crop entry.

**Endpoint:** `POST /planted_crops/update`
**Auth Required:** Yes
**Request Body:**

```json
{
  "planted_crop_id": "abc123de-4567-89fg-hijk-lmnopqrstuv0",
  "harvest_date": "2024-06-20T00:00:00Z",
  "number_of_crops": 22,
  "estimated_yield": 125.0,
  "notes": "Updated: 2 plants died due to disease"
}
```

**Note:** Only include fields you want to update. The `planted_crop_id` field is required to identify the record.

**Updatable Fields:**
- `planting_method`
- `planting_spacing`
- `germination_date`
- `transplant_date`
- `seedling_age`
- `harvest_date`
- `number_of_crops`
- `estimated_yield`
- `notes`

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "abc123de-4567-89fg-hijk-lmnopqrstuv0",
    "harvest_date": "2024-06-20T00:00:00",
    "number_of_crops": 22,
    "estimated_yield": 125.0,
    "updated_at": "2024-05-10T14:20:00",
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
  "error": "Planted crop with uuid abc123de-4567-89fg-hijk-lmnopqrstuv0 not found or access denied"
}
```

**Note:** Users can only update their own planted crops.

---

### 6. Delete Planted Crop

Delete a planted crop entry.

**Endpoint:** `POST /planted_crops/delete`
**Auth Required:** Yes
**Request Body:**

```json
{
  "planted_crop_id": "abc123de-4567-89fg-hijk-lmnopqrstuv0"
}
```

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "message": "Planted crop abc123de-4567-89fg-hijk-lmnopqrstuv0 deleted successfully"
  },
  "error": null
}
```

**Error Response:**

```json
{
  "status": "error",
  "data": null,
  "error": "Planted crop with uuid abc123de-4567-89fg-hijk-lmnopqrstuv0 not found or access denied"
}
```

**Note:** Users can only delete their own planted crops.

---

### 7. Count Planted Crops

Get the total count of planted crops for the authenticated user with optional filtering.

**Endpoint:** `POST /planted_crops/count`
**Auth Required:** Yes
**Request Body:**

```json
{
  "plot_id": "9edec237-2122-4ae9-af10-de5abe7bdc47",
  "crop_id": "8d99a668-1863-4f4b-8025-b50e66c48ff5"
}
```

**Parameters:**
- `plot_id` (optional) - Filter by plot UUID
- `crop_id` (optional) - Filter by crop UUID

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "count": 15
  },
  "error": null
}
```

---

### 8. Get Planted Crop Statistics

Get statistical information about planted crops for the authenticated user.

**Endpoint:** `POST /planted_crops/statistics`
**Auth Required:** Yes
**Request Body:** `{}` (empty object)

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "total_planted_crops": 45,
    "by_plot": [
      {"plot_id": 8, "count": 12},
      {"plot_id": 10, "count": 18},
      {"plot_id": 15, "count": 15}
    ],
    "by_crop": [
      {"crop_id": 15, "count": 20},
      {"crop_id": 22, "count": 15},
      {"crop_id": 8, "count": 10}
    ],
    "total_estimated_yield_kg": 1250.5,
    "total_plants": 380
  },
  "error": null
}
```

**Use Case:** Perfect for dashboard displays showing user's planting overview.

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

- `"crop_id and plot_id are required"` - Missing required fields
- `"Crop with uuid {uuid} not found"` - Referenced crop doesn't exist
- `"Plot with uuid {uuid} not found"` - Referenced plot doesn't exist
- `"User with uuid {uuid} not found"` - User authentication issue
- `"Cannot plant a crop in a {type} plot type"` - Invalid plot type for planting
- `"Planted crop with uuid {uuid} not found or access denied"` - Record doesn't exist or belongs to another user
- `"Invalid germination_date format"` - Date format error
- `"planted_crop_id is required"` - Missing required parameter

### HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Missing required parameters or invalid data
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - Access denied (trying to access another user's data)
- `500 Internal Server Error` - Server-side error

---

## Date Format

All date fields use ISO 8601 format:
- **With timezone:** `2024-03-15T10:30:00Z` or `2024-03-15T10:30:00+00:00`
- **Without timezone:** `2024-03-15T10:30:00`

Dates are stored in the database without timezone information (UTC assumed).

---

## Usage Examples

### Example 1: Plant a New Crop

```javascript
const response = await fetch('/planted_crops/create', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    crop_id: '8d99a668-1863-4f4b-8025-b50e66c48ff5',
    plot_id: '9edec237-2122-4ae9-af10-de5abe7bdc47',
    planting_method: 'transplant',
    germination_date: '2024-03-15T00:00:00Z',
    transplant_date: '2024-04-05T00:00:00Z',
    number_of_crops: 24,
    estimated_yield: 132.0
  })
});

const result = await response.json();
if (result.status === 'success') {
  console.log('Planted crop created:', result.data.uuid);
}
```

### Example 2: Get All Crops in a Specific Plot

```javascript
const response = await fetch('/planted_crops/get_all', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    plot_id: '9edec237-2122-4ae9-af10-de5abe7bdc47',
    limit: 50
  })
});

const result = await response.json();
if (result.status === 'success') {
  console.log('Crops in plot:', result.data);
}
```

### Example 3: Get Dashboard Statistics

```javascript
const response = await fetch('/planted_crops/statistics', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({})
});

const result = await response.json();
if (result.status === 'success') {
  const stats = result.data;
  console.log(`Total crops: ${stats.total_planted_crops}`);
  console.log(`Total plants: ${stats.total_plants}`);
  console.log(`Expected yield: ${stats.total_estimated_yield_kg} kg`);
}
```

### Example 4: Update Harvest Information

```javascript
const response = await fetch('/planted_crops/update', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    planted_crop_id: 'abc123de-4567-89fg-hijk-lmnopqrstuv0',
    harvest_date: '2024-06-20T00:00:00Z',
    notes: 'Harvested earlier than expected due to heat'
  })
});

const result = await response.json();
if (result.status === 'success') {
  console.log('Updated:', result.data);
}
```

### Example 5: Get Detailed View for Display

```javascript
const response = await fetch('/planted_crops/get_with_details', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    limit: 20
  })
});

const result = await response.json();
if (result.status === 'success') {
  result.data.forEach(item => {
    console.log(`${item.crop.common_name} in ${item.plot.name}`);
    console.log(`  - ${item.number_of_crops} plants`);
    console.log(`  - Expected yield: ${item.estimated_yield} kg`);
  });
}
```

---

## Workflow Example: Complete Planting Cycle

### Step 1: Choose a Crop
```javascript
// Search for tomato varieties
const crops = await fetch('/crops/search', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer TOKEN', 'Content-Type': 'application/json' },
  body: JSON.stringify({ search_term: 'tomato' })
});
const cropData = await crops.json();
const selectedCropId = cropData.data[0].uuid;
```

### Step 2: Select a Plot
```javascript
// Get user's plots (from Plot API)
const plots = await fetch('/plots/get_all', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer TOKEN', 'Content-Type': 'application/json' },
  body: JSON.stringify({ limit: 100 })
});
const plotData = await plots.json();
// Filter for plantable plot types
const plantablePlots = plotData.data.filter(p =>
  ['field', 'pasture', 'natural-area', 'green-house'].includes(p.plot_type)
);
const selectedPlotId = plantablePlots[0].uuid;
```

### Step 3: Plant the Crop
```javascript
const planted = await fetch('/planted_crops/create', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer TOKEN', 'Content-Type': 'application/json' },
  body: JSON.stringify({
    crop_id: selectedCropId,
    plot_id: selectedPlotId,
    planting_method: 'transplant',
    germination_date: '2024-03-15T00:00:00Z',
    number_of_crops: 24
  })
});
const plantedData = await planted.json();
```

### Step 4: Track Progress
```javascript
// Update with transplant information
await fetch('/planted_crops/update', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer TOKEN', 'Content-Type': 'application/json' },
  body: JSON.stringify({
    planted_crop_id: plantedData.data.uuid,
    transplant_date: '2024-04-05T00:00:00Z',
    seedling_age: 21
  })
});
```

### Step 5: Record Harvest
```javascript
// Update with harvest information
await fetch('/planted_crops/update', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer TOKEN', 'Content-Type': 'application/json' },
  body: JSON.stringify({
    planted_crop_id: plantedData.data.uuid,
    harvest_date: '2024-06-15T00:00:00Z',
    estimated_yield: 132.0,
    notes: 'Excellent harvest, plants were very healthy'
  })
});
```

---

## Notes for Frontend Development

1. **UUID Consistency:** Always use UUIDs for `crop_id`, `plot_id`, and `planted_crop_id` in request bodies

2. **Date Handling:**
   - Use ISO 8601 format for all dates
   - Consider using libraries like `date-fns` or `dayjs` for date formatting
   - Timezone info will be stripped on the server

3. **Plot Type Validation:**
   - Before allowing users to plant crops, validate the plot type
   - Only allow planting in: field, pasture, natural-area, green-house
   - Show clear error messages for invalid plot types

4. **User Isolation:**
   - All endpoints automatically filter by the authenticated user
   - No need to pass user_id in requests
   - Users cannot access other users' planted crops

5. **Detail Endpoints:**
   - Use `/get_with_details` when you need full crop and plot information
   - Use `/get_all` when you already have crop/plot data cached

6. **Statistics for Dashboards:**
   - Use `/statistics` endpoint for dashboard summaries
   - Cache statistics data and refresh periodically

7. **Pagination:**
   - Implement "load more" or infinite scroll using `skip` and `limit`
   - Default limit is 100, adjust based on your UI needs

8. **Form Validation:**
   - Validate required fields (crop_id, plot_id) before submission
   - Provide date pickers for date fields
   - Show helpful error messages for validation failures

9. **Error Handling:**
   - Always check `result.status` before accessing `result.data`
   - Display user-friendly error messages from `result.error`
   - Handle authentication errors by redirecting to login
