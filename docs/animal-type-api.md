# Animal Type API Documentation

## Overview

The Animal Type API provides endpoints to manage animal breed and type definitions in the FarmBros system. Animal types contain detailed information about breeds, reproductive characteristics, growth timelines, and production data that serve as templates for individual animals and batches.

**Base URL:** `/animal_types`

## Authentication

- **Admin endpoints** require admin role authentication for Create, Update, Delete operations
- **User endpoints** require standard user authentication for Read operations
- All endpoints require a valid JWT token in the Authorization header: `Bearer <token>`

## Data Model

### AnimalType Object

```json
{
  "id": 1,
  "uuid": "fc661ed3-f580-49cb-9ba8-9fd2276a4641",
  "breed": "Holstein",
  "species": "Bos taurus",
  "sex": "female",
  "category": "cattle",
  "category_type": "dairy",
  "puberty_age": 450,
  "estrus_cycle_type": "polyestrous",
  "estrus_cycle_length": 21,
  "estrus_duration": 18,
  "best_breeding_time": "12-18 hours after heat detection",
  "heat_signs": "Mounting other cows, restlessness, mucus discharge, decreased milk production",
  "age_at_first_egg": null,
  "days_to_breed": 450,
  "days_to_market": 730,
  "notes": "Top milk producer, black and white coloring",
  "created_at": "2024-11-15T10:30:00",
  "updated_at": "2024-11-15T10:30:00"
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | Integer | Auto | Internal database ID (read-only) |
| `uuid` | String | Auto | External unique identifier (UUID format) |
| `breed` | String | Yes | Animal breed name |
| `species` | String | No | Scientific species name |
| `sex` | Enum | No | Biological sex classification (see Enums) |
| `category` | Enum | Yes | Animal category/type (see Enums) |
| `category_type` | String | No | Sub-category (e.g., dairy, beef, layer, broiler) |
| `puberty_age` | Integer | No | Age at puberty in days |
| `estrus_cycle_type` | String | No | Type of estrus cycle (e.g., polyestrous, seasonal) |
| `estrus_cycle_length` | Integer | No | Length of estrus cycle in days |
| `estrus_duration` | Integer | No | Duration of heat in hours |
| `best_breeding_time` | String | No | Optimal breeding timing description |
| `heat_signs` | Text | No | Observable signs of heat/estrus |
| `age_at_first_egg` | Integer | No | For poultry, age at first egg in days |
| `days_to_breed` | Integer | No | Days from birth to breeding age |
| `days_to_market` | Integer | No | Days to reach market weight/age |
| `notes` | Text | No | Additional information |
| `created_at` | DateTime | Auto | Creation timestamp (ISO 8601) |
| `updated_at` | DateTime | Auto | Last update timestamp (ISO 8601) |

### Enums

#### AnimalCategory
- `cattle` - Cattle (cows, bulls, steers)
- `sheep` - Sheep
- `goat` - Goats
- `pig` - Pigs
- `chicken` - Chickens
- `duck` - Ducks
- `turkey` - Turkeys
- `rabbit` - Rabbits
- `fish` - Fish (aquaculture)
- `other` - Other animal types

#### AnimalSex
- `male` - Male animals
- `female` - Female animals
- `mixed` - Mixed sex groups or breeding pairs

## API Endpoints

### 1. Create Animal Type

Create a new animal type definition.

**Endpoint:** `POST /animal_types/create`
**Auth Required:** Admin only

**Request Body:**

```json
{
  "breed": "Holstein",
  "species": "Bos taurus",
  "category": "cattle",
  "sex": "female",
  "category_type": "dairy",
  "puberty_age": 450,
  "estrus_cycle_type": "polyestrous",
  "estrus_cycle_length": 21,
  "estrus_duration": 18,
  "best_breeding_time": "12-18 hours after heat detection",
  "heat_signs": "Mounting other cows, restlessness, mucus discharge",
  "days_to_breed": 450,
  "days_to_market": 730,
  "notes": "Top milk producer"
}
```

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "fc661ed3-f580-49cb-9ba8-9fd2276a4641",
    "breed": "Holstein",
    "species": "Bos taurus",
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
  "error": "breed and category are required"
}
```

**Validation Rules:**
- `breed` is required
- `category` is required and must be a valid enum value
- `sex` must be a valid enum value if provided
- All numeric fields accept positive integers
- All text fields accept strings

---

### 2. Get Animal Type

Retrieve a single animal type by UUID.

**Endpoint:** `POST /animal_types/get`
**Auth Required:** Authenticated users

**Request Body:**

```json
{
  "animal_type_id": "fc661ed3-f580-49cb-9ba8-9fd2276a4641"
}
```

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "fc661ed3-f580-49cb-9ba8-9fd2276a4641",
    "breed": "Holstein",
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
  "error": "Animal type not found"
}
```

---

### 3. Get All Animal Types

Retrieve a list of animal types with optional filtering.

**Endpoint:** `POST /animal_types/get_all`
**Auth Required:** Authenticated users

**Request Body:**

```json
{
  "skip": 0,
  "limit": 100,
  "category": "cattle",
  "sex": "female"
}
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | Integer | 0 | Number of records to skip (pagination) |
| `limit` | Integer | 100 | Maximum number of records to return |
| `category` | String | null | Filter by animal category |
| `sex` | String | null | Filter by sex |

**Success Response:**

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "uuid": "fc661ed3-f580-49cb-9ba8-9fd2276a4641",
      "breed": "Holstein",
      ...
    },
    {
      "id": 2,
      "uuid": "abc123...",
      "breed": "Angus",
      ...
    }
  ],
  "error": null
}
```

---

### 4. Update Animal Type

Update an existing animal type.

**Endpoint:** `POST /animal_types/update`
**Auth Required:** Admin only

**Request Body:**

```json
{
  "animal_type_id": "fc661ed3-f580-49cb-9ba8-9fd2276a4641",
  "days_to_market": 550,
  "estrus_cycle_length": 22,
  "notes": "Updated market age based on new feeding program"
}
```

**Note:** Only include fields you want to update. The `animal_type_id` is required.

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "uuid": "fc661ed3-f580-49cb-9ba8-9fd2276a4641",
    "breed": "Holstein",
    "days_to_market": 550,
    ...
  },
  "error": null
}
```

**Validation Rules:**
- `category` cannot be set to null (required field)
- All enum fields must use valid enum values
- Fields not included in the request remain unchanged

---

### 5. Delete Animal Type

Delete an animal type.

**Endpoint:** `POST /animal_types/delete`
**Auth Required:** Admin only

**Request Body:**

```json
{
  "animal_type_id": "fc661ed3-f580-49cb-9ba8-9fd2276a4641"
}
```

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "deleted": true,
    "animal_type_id": "fc661ed3-f580-49cb-9ba8-9fd2276a4641"
  },
  "error": null
}
```

**Error Response:**

```json
{
  "status": "error",
  "data": null,
  "error": "Animal type not found"
}
```

**Warning:** Deleting an animal type may fail if there are animals currently using this type. Consider soft-deleting or archiving instead.

---

## Common Use Cases

### Creating a Dairy Cattle Type

```json
{
  "breed": "Holstein",
  "species": "Bos taurus",
  "category": "cattle",
  "sex": "female",
  "category_type": "dairy",
  "puberty_age": 450,
  "estrus_cycle_type": "polyestrous",
  "estrus_cycle_length": 21,
  "estrus_duration": 18,
  "best_breeding_time": "12-18 hours after heat detection",
  "heat_signs": "Mounting other cows, restlessness, mucus discharge",
  "days_to_breed": 450,
  "days_to_market": 730
}
```

### Creating a Broiler Chicken Type

```json
{
  "breed": "Cornish Cross",
  "species": "Gallus gallus domesticus",
  "category": "chicken",
  "sex": "mixed",
  "category_type": "broiler",
  "days_to_market": 42,
  "notes": "Fast-growing meat chicken"
}
```

### Creating a Layer Hen Type

```json
{
  "breed": "Rhode Island Red",
  "species": "Gallus gallus domesticus",
  "category": "chicken",
  "sex": "female",
  "category_type": "layer",
  "puberty_age": 150,
  "age_at_first_egg": 150,
  "days_to_market": 540
}
```

---

## Error Handling

All endpoints return errors in a consistent format:

```json
{
  "status": "error",
  "data": null,
  "error": "Error message describing what went wrong"
}
```

### Common Error Messages

| Error Message | Cause | Solution |
|--------------|-------|----------|
| `breed and category are required` | Missing required fields | Include both `breed` and `category` |
| `Invalid category: [value]` | Invalid enum value | Use valid category from enum list |
| `Invalid sex: [value]` | Invalid enum value | Use valid sex from enum list |
| `Animal type not found` | UUID doesn't exist | Verify the UUID is correct |
| `Unauthorized` | Missing/invalid token | Provide valid admin JWT token |

---

## Best Practices

### 1. **Use Meaningful Breed Names**
- Be specific: "Holstein Friesian" instead of "Cow"
- Include regional variants if relevant

### 2. **Populate Reproductive Data for Breeding Animals**
- Essential for breeding management
- Helps with heat detection and timing

### 3. **Set Realistic Market Ages**
- `days_to_market` helps with planning and inventory
- Consider different feeding programs

### 4. **Use Category Types for Differentiation**
- "dairy" vs "beef" for cattle
- "layer" vs "broiler" for chickens
- Enables better filtering and reporting

### 5. **Include Poultry-Specific Data**
- Use `age_at_first_egg` for layers
- Critical for production planning

---

## Caching

The following endpoints use Redis caching:

- **GET ALL**: Cached for 24 hours (86400 seconds)
- Cache keys include filter parameters
- Cache automatically invalidates on Create, Update, Delete operations

---

## Notes for Frontend Developers

1. **UUID Usage**: Always use the `uuid` field (not `id`) for API requests
2. **Required Fields**: Only `breed` and `category` are required for creation
3. **Enums**: Validate enum values client-side before submission
4. **Admin Access**: Create, Update, Delete require admin role
5. **Filtering**: Use `category` and `sex` filters for dropdown lists
6. **Pagination**: Default limit is 100, use skip/limit for large lists
7. **Immutable `category`**: Once set, category is required and cannot be null
8. **Optional Fields**: All other fields are optional and can be added/updated later
