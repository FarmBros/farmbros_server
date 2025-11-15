# Farm API Documentation

## Overview

The Farm API provides endpoints to manage farm properties in the FarmBros system. Farms are geospatial entities with polygon boundaries, owned by users, and contain plots. All farm boundaries and locations are stored using PostGIS geography types with SRID 4326 (WGS 84).

**Base URL:** `/farms`

## Authentication

- All endpoints require user authentication
- JWT token required in Authorization header: `Bearer <token>`
- Users can only manage their own farms

## Data Model

### Farm Object

```json
{
  "id": 1,
  "uuid": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "name": "Green Valley Farm",
  "owner_id": "user-uuid-here",
  "description": "100-acre family farm specializing in organic vegetables",
  "area_sqm": 404685.642,
  "created_at": "2024-11-15T10:30:00",
  "updated_at": "2024-11-15T10:30:00",
  "boundary": {
    "type": "Polygon",
    "coordinates": [
      [
        [-122.084, 37.422],
        [-122.083, 37.422],
        [-122.083, 37.421],
        [-122.084, 37.421],
        [-122.084, 37.422]
      ]
    ]
  },
  "centroid": {
    "type": "Point",
    "coordinates": [-122.0835, 37.4215]
  }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Internal database ID (read-only) |
| `uuid` | String | External unique identifier (UUID format) |
| `name` | String | Name of the farm (required) |
| `owner_id` | String | UUID of the user who owns the farm |
| `description` | Text | Detailed description of the farm |
| `area_sqm` | Float | Farm area in square meters (auto-calculated from boundary) |
| `created_at` | DateTime | Creation timestamp (ISO 8601) |
| `updated_at` | DateTime | Last update timestamp (ISO 8601) |
| `boundary` | GeoJSON | Farm boundary as GeoJSON Polygon (SRID 4326) |
| `centroid` | GeoJSON | Farm center point as GeoJSON Point (SRID 4326) |

### Area Conversions

- **Square meters to hectares:** `area_sqm / 10000`
- **Square meters to acres:** `area_sqm / 4047`

---

## API Endpoints

### 1. Create Farm

Create a new farm with geospatial boundary.

**Endpoint:** `POST /farms/create`
**Auth Required:** Yes
**Request Body:**

```json
{
  "name": "Green Valley Farm",
  "description": "Organic vegetable farm",
  "boundary_geojson": {
    "type": "Polygon",
    "coordinates": [
      [
        [-122.084, 37.422],
        [-122.083, 37.422],
        [-122.083, 37.421],
        [-122.084, 37.421],
        [-122.084, 37.422]
      ]
    ]
  }
}
```

**Required Fields:**
- `name` - Farm name
- `boundary_geojson` - GeoJSON Polygon defining farm boundary

**Optional Fields:**
- `description` - Farm description

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
    "name": "Green Valley Farm",
    "owner_id": "user-uuid-here",
    "description": "Organic vegetable farm",
    "area_sqm": 404685.642,
    "created_at": "2024-11-15T10:30:00",
    "updated_at": "2024-11-15T10:30:00"
  },
  "error": null
}
```

**Error Response:**

```json
{
  "status": "error",
  "data": null,
  "error": "name and boundary_geojson are required"
}
```

**Notes:**
- Boundary must be a valid GeoJSON Polygon
- Area is automatically calculated from the boundary
- Centroid is automatically calculated
- Owner is set from the authenticated user's token

---

### 2. Get Farm

Retrieve a single farm by UUID.

**Endpoint:** `POST /farms/get_farm`
**Auth Required:** Yes
**Request Body:**

```json
{
  "farm_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "include_geojson": true
}
```

**Parameters:**
- `farm_id` (required) - UUID of the farm
- `include_geojson` (optional, default: false) - Include boundary and centroid GeoJSON

**Success Response (with GeoJSON):**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
    "name": "Green Valley Farm",
    "owner_id": "user-uuid-here",
    "description": "Organic vegetable farm",
    "area_sqm": 404685.642,
    "created_at": "2024-11-15T10:30:00",
    "updated_at": "2024-11-15T10:30:00",
    "boundary": {
      "type": "Polygon",
      "coordinates": [[[-122.084, 37.422], [-122.083, 37.422], ...]]
    },
    "centroid": {
      "type": "Point",
      "coordinates": [-122.0835, 37.4215]
    }
  },
  "error": null
}
```

---

### 3. Get All Farms

Retrieve all farms in the system with pagination.

**Endpoint:** `POST /farms/get_all_farms`
**Auth Required:** Yes
**Request Body:**

```json
{
  "skip": 0,
  "limit": 100,
  "include_geojson": false
}
```

**Parameters:**
- `skip` (optional, default: 0) - Number of records to skip for pagination
- `limit` (optional, default: 100) - Maximum number of records to return
- `include_geojson` (optional, default: false) - Include boundary and centroid GeoJSON

**Success Response:**

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "uuid": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
      "name": "Green Valley Farm",
      ...
    },
    {
      "id": 2,
      "uuid": "b2c3d4e5-6789-01bc-defg-234567890abc",
      "name": "Sunset Ranch",
      ...
    }
  ],
  "error": null
}
```

---

### 4. Get User Farms

Retrieve all farms owned by the authenticated user.

**Endpoint:** `POST /farms/get_user_farms`
**Auth Required:** Yes
**Request Body:** `{}` (empty object)

**Success Response:**

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "uuid": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
      "name": "Green Valley Farm",
      "owner_id": "authenticated-user-uuid",
      "area_sqm": 404685.642,
      ...
    }
  ],
  "error": null
}
```

**Use Case:** Get all farms for the current user's dashboard.

---

### 5. Update Farm

Update an existing farm's details.

**Endpoint:** `POST /farms/update_farm`
**Auth Required:** Yes
**Request Body:**

```json
{
  "farm_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "name": "Green Valley Organic Farm",
  "description": "Updated description",
  "boundary_geojson": {
    "type": "Polygon",
    "coordinates": [...]
  }
}
```

**Required Fields:**
- `farm_id` - UUID of the farm to update

**Optional Fields (update only what's provided):**
- `name` - New farm name
- `description` - New description
- `boundary_geojson` - New boundary (area will be recalculated)

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
    "name": "Green Valley Organic Farm",
    "description": "Updated description",
    "updated_at": "2024-11-15T15:45:00",
    ...
  },
  "error": null
}
```

**Notes:**
- Only the farm owner can update the farm
- If boundary is updated, area and centroid are recalculated automatically

---

### 6. Delete Farm

Delete a farm and all its associated plots.

**Endpoint:** `POST /farms/delete_farm`
**Auth Required:** Yes
**Request Body:**

```json
{
  "farm_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab"
}
```

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "message": "Farm deleted successfully"
  },
  "error": null
}
```

**Warning:** This will cascade delete all plots associated with the farm!

---

### 7. Get Farm Statistics

Get statistical information about farms.

**Endpoint:** `POST /farms/get_farm_stats`
**Auth Required:** Yes
**Request Body:**

```json
{
  "owner_id": "user-uuid-here"
}
```

**Parameters:**
- `owner_id` (optional) - Filter stats by owner UUID

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "total_farms": 5,
    "total_area_sqm": 2023428.21,
    "total_area_hectares": 202.34,
    "total_area_acres": 500.0,
    "farms_by_owner": [
      {"owner_id": "user-uuid-1", "count": 3},
      {"owner_id": "user-uuid-2", "count": 2}
    ]
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

- `"name and boundary_geojson are required"` - Missing required fields
- `"farm_id is required"` - Missing farm identifier
- `"Farm not found"` - Farm doesn't exist or access denied
- `"Invalid GeoJSON format"` - Malformed boundary geometry
- `"User does not own this farm"` - Authorization error

### HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Missing required parameters or invalid data
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - User doesn't own the farm
- `404 Not Found` - Farm not found
- `500 Internal Server Error` - Server-side error

---

## GeoJSON Format

### Polygon Format (Farm Boundary)

```json
{
  "type": "Polygon",
  "coordinates": [
    [
      [longitude1, latitude1],
      [longitude2, latitude2],
      [longitude3, latitude3],
      [longitude4, latitude4],
      [longitude1, latitude1]
    ]
  ]
}
```

**Important Notes:**
- Coordinates are `[longitude, latitude]` (NOT latitude, longitude)
- First and last points must be identical (closed polygon)
- Minimum 4 points (3 unique corners + closing point)
- Uses WGS 84 coordinate system (SRID 4326)

### Point Format (Centroid)

```json
{
  "type": "Point",
  "coordinates": [longitude, latitude]
}
```

---

## Usage Examples

### Example 1: Create a Farm

```javascript
const response = await fetch('/farms/create', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Sunrise Organic Farm',
    description: '50-acre certified organic farm',
    boundary_geojson: {
      type: 'Polygon',
      coordinates: [[
        [-122.084, 37.422],
        [-122.083, 37.422],
        [-122.083, 37.421],
        [-122.084, 37.421],
        [-122.084, 37.422]
      ]]
    }
  })
});

const result = await response.json();
if (result.status === 'success') {
  console.log('Farm created:', result.data.uuid);
  console.log('Area:', result.data.area_sqm / 10000, 'hectares');
}
```

### Example 2: Get User's Farms

```javascript
const response = await fetch('/farms/get_user_farms', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({})
});

const result = await response.json();
if (result.status === 'success') {
  result.data.forEach(farm => {
    console.log(`${farm.name}: ${(farm.area_sqm / 10000).toFixed(2)} ha`);
  });
}
```

### Example 3: Get Farm with Boundary for Map Display

```javascript
const response = await fetch('/farms/get_farm', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    farm_id: 'a1b2c3d4-5678-90ab-cdef-1234567890ab',
    include_geojson: true
  })
});

const result = await response.json();
if (result.status === 'success') {
  // Use result.data.boundary to draw on map
  const farmBoundary = result.data.boundary;
  const farmCenter = result.data.centroid;

  // Add to Leaflet/MapBox/Google Maps
  map.addLayer(farmBoundary);
  map.setCenter(farmCenter.coordinates);
}
```

### Example 4: Update Farm Boundary

```javascript
const newBoundary = {
  type: 'Polygon',
  coordinates: [[
    // New coordinates after surveying
    [-122.085, 37.423],
    [-122.082, 37.423],
    [-122.082, 37.420],
    [-122.085, 37.420],
    [-122.085, 37.423]
  ]]
};

const response = await fetch('/farms/update_farm', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    farm_id: 'a1b2c3d4-5678-90ab-cdef-1234567890ab',
    boundary_geojson: newBoundary,
    description: 'Boundary updated after professional survey'
  })
});

const result = await response.json();
if (result.status === 'success') {
  console.log('New area:', result.data.area_sqm / 10000, 'hectares');
}
```

---

## Notes for Frontend Development

1. **UUID Usage:** Always use the `uuid` field when referencing farms in other API calls

2. **GeoJSON Libraries:**
   - Use libraries like Turf.js for GeoJSON manipulation
   - Validate GeoJSON before sending to API
   - Ensure polygons are properly closed

3. **Map Integration:**
   - Request `include_geojson: true` only when displaying on maps
   - Cache boundary data to reduce API calls
   - Use centroid for initial map positioning

4. **Area Display:**
   - Convert `area_sqm` to user-friendly units (hectares or acres)
   - Format large numbers appropriately (use commas or separators)

5. **Ownership:**
   - Users can only modify farms they own
   - Check ownership before showing edit/delete UI

6. **Performance:**
   - Use pagination for farm lists
   - Set `include_geojson: false` for list views to reduce payload size
   - Only fetch geometry when needed for map display

7. **Delete Confirmation:**
   - Always confirm before deleting (cascade deletes plots!)
   - Warn users about data loss

8. **Validation:**
   - Validate polygon has at least 4 points
   - Ensure first and last coordinates match
   - Check coordinate order [longitude, latitude]
