# FarmBros API Documentation

Complete API documentation for the FarmBros agricultural management system.

## Documentation Index

### Core Resources

1. **[User Management API](./user-api.md)**
   - User registration and authentication
   - Password and Google OAuth login
   - Role-based access control
   - Token management

2. **[Farm API](./farm-api.md)**
   - Farm creation and management
   - Geospatial boundaries (PostGIS)
   - Area calculations
   - Farm statistics

3. **[Plot API](./plot-api.md)**
   - Plot subdivision management
   - 10 different plot types
   - Type-specific data fields
   - Geospatial boundaries
   - Plantable vs non-plantable plots

4. **[Crop API](./crop-api.md)**
   - Crop definitions database
   - Growth characteristics
   - Nutrient requirements
   - Yield information
   - Search and filtering

5. **[Planted Crop API](./planted-crop-api.md)**
   - Planting management
   - Timeline tracking (germination, transplant, harvest)
   - Yield estimation
   - Plot type restrictions
   - Statistics and reporting

## Quick Start

### Authentication

All API endpoints (except user registration and login) require authentication:

```javascript
headers: {
  'Authorization': 'Bearer YOUR_JWT_TOKEN',
  'Content-Type': 'application/json'
}
```

### API Base URL

Development: `http://localhost:8000`
Production: `https://your-domain.com`

### Common Response Format

All endpoints return responses in this format:

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
  "error": "Error message"
}
```

## Data Hierarchy

```
User
├── Farm (multiple)
│   └── Plot (multiple)
│       └── PlantedCrop (multiple)
│           └── Crop (reference)
```

## UUID Convention

**All request body keys use the `_id` suffix with UUID values:**

```json
{
  "farm_id": "uuid-here",
  "plot_id": "uuid-here",
  "crop_id": "uuid-here",
  "planted_crop_id": "uuid-here",
  "user_id": "uuid-here"
}
```

## Key Concepts

### Geospatial Data

- All geometries use **SRID 4326** (WGS 84)
- Coordinates are `[longitude, latitude]` order
- Boundaries are GeoJSON Polygons
- Areas calculated in square meters

### Plot Types

| Type | Can Plant Crops | Primary Use |
|------|----------------|-------------|
| field | ✅ Yes | Crop cultivation |
| pasture | ✅ Yes | Livestock grazing |
| green-house | ✅ Yes | Controlled cultivation |
| natural-area | ✅ Yes | Conservation |
| barn | ❌ No | Storage/shelter |
| chicken-pen | ❌ No | Poultry farming |
| cow-shed | ❌ No | Cattle housing |
| fish-pond | ❌ No | Aquaculture |
| residence | ❌ No | Living quarters |
| water-source | ❌ No | Water supply |

### User Roles

- **user** - Standard user (manages own farms/plots/crops)
- **admin** - Administrator (access to crop database management, statistics)

## Typical Workflows

### 1. User Registration & Login

```
1. POST /users/create (or /users/google_signup)
2. POST /users/login
3. Store JWT token
4. Use token for all subsequent requests
```

### 2. Farm Setup

```
1. POST /farms/create (with boundary GeoJSON)
2. POST /plots/create (multiple plots within farm)
3. Set plot types and type-specific data
```

### 3. Crop Planting

```
1. POST /crops/search (find crop to plant)
2. GET /plots/get_plots_by_farm (get available plots)
3. Filter plots by plantable types (field, pasture, greenhouse, natural-area)
4. POST /planted_crops/create
5. Track growth with POST /planted_crops/update
```

### 4. Harvest & Statistics

```
1. POST /planted_crops/update (set harvest_date, actual yield)
2. POST /planted_crops/statistics (view overall stats)
3. POST /farms/get_farm_stats (farm-level statistics)
```

## Integration Examples

### Complete Farm Creation Flow

```javascript
// 1. Create farm
const farm = await createFarm({
  name: 'Green Valley Farm',
  boundary_geojson: { ... }
});

// 2. Create plots
const fieldPlot = await createPlot({
  farm_id: farm.uuid,
  name: 'North Field',
  plot_type: 'field',
  boundary_geojson: { ... },
  plot_type_data: {
    soil_type: 'Loamy',
    irrigation_system: 'Drip'
  }
});

const greenhousePlot = await createPlot({
  farm_id: farm.uuid,
  name: 'Greenhouse A',
  plot_type: 'green-house',
  boundary_geojson: { ... },
  plot_type_data: {
    greenhouse_type: 'Glass greenhouse'
  }
});

// 3. Search and plant crops
const tomato = await searchCrop('tomato');

const plantedCrop = await plantCrop({
  crop_id: tomato.uuid,
  plot_id: fieldPlot.uuid,
  number_of_crops: 50,
  planting_method: 'transplant'
});
```

## Error Handling

### HTTP Status Codes

- `200 OK` - Success
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required/failed
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Duplicate entry
- `500 Internal Server Error` - Server error

### Common Patterns

```javascript
async function apiCall(endpoint, data) {
  const token = localStorage.getItem('access_token');

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });

    if (response.status === 401) {
      // Token expired, redirect to login
      window.location.href = '/login';
      return;
    }

    const result = await response.json();

    if (result.status === 'error') {
      throw new Error(result.error);
    }

    return result.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}
```

## Performance Tips

1. **Pagination** - Use `skip` and `limit` parameters for large lists
2. **GeoJSON** - Set `include_geojson: false` for list views
3. **Caching** - Cache crop definitions and static data
4. **Batch Operations** - Group related API calls when possible
5. **Lazy Loading** - Load geometries only when displaying maps

## Testing Endpoints

Use the provided `.http` files in the `endpoints/` directory:

- `endpoints/user_endpoints.http`
- `endpoints/farm_endpoints.http`
- `endpoints/plot_endpoints.http`
- `endpoints/crop_endpoints.http`
- `endpoints/planted_crop_endpoints.http`

## Support

- API Issues: Check error messages and HTTP status codes
- Authentication Issues: Verify token validity with `/users/me`
- Geospatial Issues: Validate GeoJSON format before submission
- Permission Issues: Check user role and ownership

## Changelog

### Latest Updates

- Added plot type validation for crop planting
- Comprehensive API documentation
- GeoJSON support for boundaries
- Statistics endpoints for reporting
- Google OAuth integration

## Additional Resources

- PostGIS Documentation: https://postgis.net/
- GeoJSON Specification: https://geojson.org/
- JWT Authentication: https://jwt.io/
- FastAPI Documentation: https://fastapi.tiangolo.com/
