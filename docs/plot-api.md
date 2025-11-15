# Plot API Documentation

## Overview

The Plot API provides endpoints to manage plot subdivisions within farms. Plots are geospatial entities with polygon boundaries and specific types (field, barn, pasture, greenhouse, etc.). Each plot type has additional specialized data fields. All boundaries are stored using PostGIS geography types with SRID 4326.

**Base URL:** `/plots`

## Authentication

- All endpoints require user authentication
- JWT token required in Authorization header: `Bearer <token>`
- Users can only manage plots on their own farms

## Data Model

### Plot Object

```json
{
  "id": 1,
  "uuid": "9edec237-2122-4ae9-af10-de5abe7bdc47",
  "name": "North Field",
  "farm_id": 5,
  "plot_number": "A1",
  "plot_type": "field",
  "area_sqm": 10000.0,
  "notes": "Main vegetable growing area",
  "created_at": "2024-11-15T10:30:00",
  "updated_at": "2024-11-15T10:30:00",
  "boundary": {
    "type": "Polygon",
    "coordinates": [[...]]
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
| `name` | String | Name of the plot (required) |
| `farm_id` | Integer | Internal farm reference (read-only) |
| `plot_number` | String | Human-friendly plot identifier (e.g., "A1", "B3") |
| `plot_type` | Enum | Type of plot (see Plot Types section) |
| `area_sqm` | Float | Plot area in square meters (auto-calculated) |
| `notes` | Text | Additional information |
| `created_at` | DateTime | Creation timestamp (ISO 8601) |
| `updated_at` | DateTime | Last update timestamp (ISO 8601) |
| `boundary` | GeoJSON | Plot boundary as GeoJSON Polygon (SRID 4326) |
| `centroid` | GeoJSON | Plot center point as GeoJSON Point |

### Plot Types

| Type | Value | Description | Can Plant Crops |
|------|-------|-------------|-----------------|
| Field | `field` | Crop cultivation area | ✅ Yes |
| Barn | `barn` | Equipment and livestock shelter | ❌ No |
| Pasture | `pasture` | Livestock grazing area | ✅ Yes |
| Greenhouse | `green-house` | Controlled environment cultivation | ✅ Yes |
| Chicken Pen | `chicken-pen` | Poultry farming area | ❌ No |
| Cow Shed | `cow-shed` | Cattle housing | ❌ No |
| Fish Pond | `fish-pond` | Aquaculture area | ❌ No |
| Residence | `residence` | Living quarters | ❌ No |
| Natural Area | `natural-area` | Conservation area | ✅ Yes |
| Water Source | `water-source` | Wells, springs, water storage | ❌ No |

### Plot Type Data

Each plot type has additional specialized fields:

#### Field Plot Type
```json
{
  "soil_type": "Loamy",
  "irrigation_system": "Drip irrigation"
}
```

#### Barn Plot Type
```json
{
  "structure_type": "Pole barn"
}
```

#### Pasture Plot Type
```json
{
  "status": "Active"
}
```

#### Greenhouse Plot Type
```json
{
  "greenhouse_type": "Hoop house"
}
```

#### Chicken Pen Plot Type
```json
{
  "chicken_capacity": 50,
  "coop_type": "Free-range",
  "nesting_boxes": 12,
  "run_area_covered": "Yes",
  "feeding_system": "Automatic feeders"
}
```

#### Cow Shed Plot Type
```json
{
  "cow_capacity": 20,
  "milking_system": "Automated milking",
  "feeding_system": "TMR mixer",
  "bedding_type": "Sand",
  "waste_management": "Slurry system"
}
```

#### Fish Pond Plot Type
```json
{
  "pond_depth": "2-3 meters",
  "filtration_system": "Bio-filter",
  "aeration_system": "Air stones"
}
```

#### Residence Plot Type
```json
{
  "building_type": "Farmhouse"
}
```

#### Natural Area Plot Type
```json
{
  "ecosystem_type": "Woodland"
}
```

#### Water Source Plot Type
```json
{
  "source_type": "Well",
  "depth": "50 meters"
}
```

---

## API Endpoints

### 1. Create Plot

Create a new plot within a farm.

**Endpoint:** `POST /plots/create`
**Auth Required:** Yes
**Request Body:**

```json
{
  "farm_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "name": "North Field",
  "plot_number": "A1",
  "plot_type": "field",
  "boundary_geojson": {
    "type": "Polygon",
    "coordinates": [[...]]
  },
  "notes": "Main vegetable growing area",
  "plot_type_data": {
    "soil_type": "Loamy",
    "irrigation_system": "Drip irrigation"
  }
}
```

**Required Fields:**
- `farm_id` - UUID of the parent farm
- `name` - Plot name
- `boundary_geojson` - GeoJSON Polygon

**Optional Fields:**
- `plot_number` - Human-friendly identifier
- `plot_type` - Type enum (default: "field")
- `notes` - Additional information
- `plot_type_data` - Type-specific data (see Plot Type Data section)

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "9edec237-2122-4ae9-af10-de5abe7bdc47",
    "name": "North Field",
    "farm_id": 5,
    "plot_type": "field",
    "area_sqm": 10000.0,
    ...
  },
  "error": null
}
```

---

### 2. Get Plot

Retrieve a single plot by UUID.

**Endpoint:** `POST /plots/get_plot`
**Auth Required:** Yes
**Request Body:**

```json
{
  "plot_id": "9edec237-2122-4ae9-af10-de5abe7bdc47",
  "include_geojson": true
}
```

**Parameters:**
- `plot_id` (required) - UUID of the plot
- `include_geojson` (optional, default: true) - Include boundary and centroid

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "9edec237-2122-4ae9-af10-de5abe7bdc47",
    "name": "North Field",
    "plot_type": "field",
    "area_sqm": 10000.0,
    "boundary": {...},
    "centroid": {...},
    ...
  },
  "error": null
}
```

---

### 3. Get Plots by Farm

Retrieve all plots within a specific farm.

**Endpoint:** `POST /plots/get_plots_by_farm`
**Auth Required:** Yes
**Request Body:**

```json
{
  "farm_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "include_geojson": true,
  "skip": 0,
  "limit": 100
}
```

**Parameters:**
- `farm_id` (required) - UUID of the farm
- `include_geojson` (optional, default: true) - Include geometries
- `skip` (optional, default: 0) - Pagination offset
- `limit` (optional, default: 100) - Max records to return

**Success Response:**

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "uuid": "9edec237-2122-4ae9-af10-de5abe7bdc47",
      "name": "North Field",
      "plot_type": "field",
      ...
    },
    {
      "id": 2,
      "uuid": "8fdec237-3233-5be0-bg21-ef6bcf8edc58",
      "name": "Greenhouse A",
      "plot_type": "green-house",
      ...
    }
  ],
  "error": null
}
```

---

### 4. Get User Plots

Retrieve all plots owned by the authenticated user (across all their farms).

**Endpoint:** `POST /plots/get_user_plots`
**Auth Required:** Yes
**Request Body:**

```json
{
  "include_geojson": false,
  "skip": 0,
  "limit": 100
}
```

**Success Response:**

```json
{
  "status": "success",
  "data": [
    {...plot1...},
    {...plot2...}
  ],
  "error": null
}
```

---

### 5. Get Plots by Type

Retrieve all plots of a specific type for the authenticated user.

**Endpoint:** `POST /plots/get_plots_by_type`
**Auth Required:** Yes
**Request Body:**

```json
{
  "plot_type": "field",
  "include_geojson": false,
  "skip": 0,
  "limit": 100
}
```

**Parameters:**
- `plot_type` (required) - Plot type enum value
- `include_geojson` (optional, default: true)
- `skip` (optional, default: 0)
- `limit` (optional, default: 100)

**Success Response:**

```json
{
  "status": "success",
  "data": [
    {...all field plots...}
  ],
  "error": null
}
```

**Use Case:** Get all greenhouse plots, all pastures, etc.

---

### 6. Update Plot

Update an existing plot's details.

**Endpoint:** `POST /plots/update_plot`
**Auth Required:** Yes
**Request Body:**

```json
{
  "plot_id": "9edec237-2122-4ae9-af10-de5abe7bdc47",
  "name": "North Field - Organic",
  "plot_number": "A1",
  "plot_type": "field",
  "notes": "Converted to organic",
  "boundary_geojson": {...},
  "plot_type_data": {
    "soil_type": "Loamy",
    "irrigation_system": "Drip irrigation"
  }
}
```

**Required Fields:**
- `plot_id` - UUID of the plot to update

**Optional Fields:**
- All other fields are optional, only provided fields will be updated

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "9edec237-2122-4ae9-af10-de5abe7bdc47",
    "name": "North Field - Organic",
    "updated_at": "2024-11-15T15:45:00",
    ...
  },
  "error": null
}
```

---

### 7. Delete Plot

Delete a plot.

**Endpoint:** `POST /plots/delete_plot`
**Auth Required:** Yes
**Request Body:**

```json
{
  "plot_id": "9edec237-2122-4ae9-af10-de5abe7bdc47"
}
```

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "message": "Plot deleted successfully"
  },
  "error": null
}
```

**Warning:** This will also delete any planted crops in this plot!

---

### 8. Count Plots by Farm

Get the total number of plots in a farm.

**Endpoint:** `POST /plots/count_plots_by_farm`
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
    "count": 15
  },
  "error": null
}
```

---

### 9. Get Plot Area by Farm

Calculate total plot area within a farm.

**Endpoint:** `POST /plots/get_plot_area_by_farm`
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
    "total_area_sqm": 50000.0,
    "total_area_hectares": 5.0,
    "total_area_acres": 12.36
  },
  "error": null
}
```

---

### 10. Get Plot Statistics

Get detailed statistics about plots.

**Endpoint:** `POST /plots/get_plot_stats`
**Auth Required:** Yes
**Request Body:**

```json
{
  "user_id": "user-uuid-here",
  "farm_id": "farm-uuid-here"
}
```

**Parameters:**
- `user_id` (optional) - Filter by user UUID
- `farm_id` (optional) - Filter by farm UUID

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "total_plots": 25,
    "by_type": [
      {"plot_type": "field", "count": 10},
      {"plot_type": "pasture", "count": 5},
      {"plot_type": "green-house", "count": 3},
      {"plot_type": "barn", "count": 2}
    ],
    "total_area_sqm": 150000.0,
    "average_plot_size_sqm": 6000.0
  },
  "error": null
}
```

---

### 11. Get Plot Type Data

Retrieve a plot with its type-specific data included.

**Endpoint:** `POST /plots/get_plot_type_data`
**Auth Required:** Yes
**Request Body:**

```json
{
  "plot_id": "9edec237-2122-4ae9-af10-de5abe7bdc47"
}
```

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "9edec237-2122-4ae9-af10-de5abe7bdc47",
    "name": "North Field",
    "plot_type": "field",
    "plot_type_data": {
      "id": 1,
      "uuid": "type-uuid-here",
      "plot_id": "9edec237-2122-4ae9-af10-de5abe7bdc47",
      "soil_type": "Loamy",
      "irrigation_system": "Drip irrigation",
      "type": "field"
    },
    ...
  },
  "error": null
}
```

---

### 12. Update Plot Type Data

Update only the type-specific data for a plot.

**Endpoint:** `POST /plots/update_plot_type_data`
**Auth Required:** Yes
**Request Body:**

```json
{
  "plot_id": "9edec237-2122-4ae9-af10-de5abe7bdc47",
  "plot_type_data": {
    "soil_type": "Clay loam",
    "irrigation_system": "Sprinkler system"
  }
}
```

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "message": "Plot type data updated successfully",
    "plot_type_data": {
      "soil_type": "Clay loam",
      "irrigation_system": "Sprinkler system",
      ...
    }
  },
  "error": null
}
```

---

## Error Handling

### Common Error Messages

- `"plot_id is required"` - Missing plot identifier
- `"farm_id is required"` - Missing farm identifier
- `"Plot not found"` - Plot doesn't exist or access denied
- `"Farm not found"` - Referenced farm doesn't exist
- `"User does not own this farm"` - Authorization error
- `"Invalid plot_type value"` - Invalid plot type enum
- `"Cannot plant a crop in a {type} plot type"` - Attempting to plant in non-plantable plot
- `"Invalid GeoJSON format"` - Malformed boundary geometry

---

## Usage Examples

### Example 1: Create a Field Plot with Type Data

```javascript
const response = await fetch('/plots/create', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    farm_id: 'a1b2c3d4-5678-90ab-cdef-1234567890ab',
    name: 'North Field',
    plot_number: 'A1',
    plot_type: 'field',
    boundary_geojson: {
      type: 'Polygon',
      coordinates: [[
        [-122.084, 37.422],
        [-122.083, 37.422],
        [-122.083, 37.421],
        [-122.084, 37.421],
        [-122.084, 37.422]
      ]]
    },
    plot_type_data: {
      soil_type: 'Loamy',
      irrigation_system: 'Drip irrigation'
    }
  })
});

const result = await response.json();
if (result.status === 'success') {
  console.log('Plot created:', result.data.uuid);
  console.log('Area:', result.data.area_sqm, 'sqm');
}
```

### Example 2: Get All Field Plots for Planting

```javascript
// Get only field-type plots suitable for crop planting
const response = await fetch('/plots/get_plots_by_type', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    plot_type: 'field',
    include_geojson: false
  })
});

const result = await response.json();
if (result.status === 'success') {
  const plantablePlots = result.data;
  console.log('Available plots for planting:', plantablePlots.length);
}
```

### Example 3: Filter Plantable Plots

```javascript
// Get all plots and filter for those that can have crops planted
const plotTypesAllowingCrops = ['field', 'pasture', 'green-house', 'natural-area'];

const response = await fetch('/plots/get_user_plots', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ include_geojson: false })
});

const result = await response.json();
if (result.status === 'success') {
  const plantablePlots = result.data.filter(plot =>
    plotTypesAllowingCrops.includes(plot.plot_type)
  );

  console.log('Plantable plots:', plantablePlots.length);
}
```

### Example 4: Display Farm Plots on Map

```javascript
const response = await fetch('/plots/get_plots_by_farm', {
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
  result.data.forEach(plot => {
    // Color code by plot type
    const color = getColorByPlotType(plot.plot_type);

    // Add to map
    map.addPolygon({
      coordinates: plot.boundary.coordinates,
      fillColor: color,
      label: `${plot.plot_number}: ${plot.name}`
    });
  });
}

function getColorByPlotType(type) {
  const colors = {
    'field': '#90EE90',
    'pasture': '#98FB98',
    'green-house': '#7FFF00',
    'barn': '#8B4513',
    'residence': '#FF6347'
  };
  return colors[type] || '#CCCCCC';
}
```

### Example 5: Update Greenhouse Type Data

```javascript
const response = await fetch('/plots/update_plot_type_data', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    plot_id: '9edec237-2122-4ae9-af10-de5abe7bdc47',
    plot_type_data: {
      greenhouse_type: 'Glass greenhouse with climate control'
    }
  })
});

const result = await response.json();
if (result.status === 'success') {
  console.log('Greenhouse type updated successfully');
}
```

---

## Notes for Frontend Development

1. **Plot Type Validation:**
   - Only allow crop planting in: field, pasture, green-house, natural-area
   - Show appropriate UI based on plot type
   - Validate plot type before showing "Plant Crop" button

2. **Type-Specific Forms:**
   - Show different form fields based on selected plot_type
   - Each plot type has unique fields (see Plot Type Data section)
   - Validate type-specific data before submission

3. **Map Display:**
   - Color-code plots by type for visual differentiation
   - Show plot_number as labels on map
   - Use centroid for plot labels/markers

4. **GeoJSON Management:**
   - Set `include_geojson: false` for list views to reduce payload
   - Only fetch geometry when displaying on maps
   - Cache plot boundaries client-side

5. **Area Display:**
   - Convert area_sqm to user-friendly units
   - Show area in both metric and imperial if needed
   - Format: "2.5 ha (6.2 acres)"

6. **Farm Context:**
   - Always work within a farm context (select farm first)
   - Show farm name/info when managing plots
   - Group plots by farm in UI

7. **Performance:**
   - Use pagination for large plot lists
   - Lazy load plot geometries
   - Cache plot type options

8. **Workflow:**
   - Farm → Plots → Planted Crops (hierarchical navigation)
   - Ensure farm exists before creating plots
   - Validate plot exists before planting crops
