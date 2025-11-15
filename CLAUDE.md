# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

FarmBros Server is a FastAPI-based agricultural management system built with:
- **FastAPI** web framework with async/await support
- **PostgreSQL** with PostGIS for geospatial data
- **SQLAlchemy 2.0** ORM with async support
- **Alembic** for database migrations
- **GeoAlchemy2** for PostGIS geometry handling

### Core Structure
```
controllers/     # Business logic and CRUD operations
models/          # SQLAlchemy models (User, Farm, Plot)
routes/          # FastAPI route definitions
services/        # Validation and utility services
alembic/         # Database migration scripts
```

### Key Models
- **User**: Authentication with roles, profiles, security features
- **Farm**: Geospatial polygons with PostGIS GEOGRAPHY fields
- **Plot**: Sub-divisions of farms with geospatial boundaries
- **Crop**: Agricultural crop definitions with growth characteristics, nutrient needs, and yield data
- **PlantedCrop**: Instances of crops planted in plots by users, tracking planting dates, methods, and expected yields

### Database Configuration
- Uses async PostgreSQL connection via `asyncpg`
- Connection configured through environment variables in `models/runner.py`
- PostGIS enabled for geospatial operations with SRID 4326

## Development Commands

### Environment Setup
```bash
# Install dependencies with uv
uv sync

# Set up database (requires PostgreSQL with PostGIS)
python database.py

# Alternative: use FastAPI endpoint
# Start server and visit /db endpoint
```

### Database Operations
```bash
# Generate new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Running the Server
```bash
# Development server
uvicorn main:app --reload

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Code Quality
```bash
# Lint with ruff
ruff check .

# Format with ruff
ruff format .
```

## Development Notes

### Database Connection
- Database URL configured via environment variables (DB_USER, DB_PASS, DB_NAME, DB_HOST)
- Hardcoded connection in `alembic.ini` should be updated for production
- Uses async sessions throughout the application

### Geospatial Features
- Farm boundaries stored as PostGIS POLYGON with SRID 4326
- Centroids auto-calculated for location queries
- Area calculations in square meters with conversion helpers
- GeoJSON serialization support for boundaries and centroids

### Authentication Pattern
- User model includes comprehensive auth features (password hashing, tokens, account locking)
- JWT tokens expected but authentication middleware not yet implemented
- Role-based access control ready for implementation

### Return types
- All controllers return a dict type with status: success, data: data, error: none for successful calls and status:error and error:str(e) for error ones

### UUID Convention
- **IMPORTANT**: Always use UUIDs (not integer IDs) for all user-facing operations and comparisons
- All models have both `id` (integer, internal) and `uuid` (string, external) fields

#### JSON API Keys
- **JSON body keys ALWAYS use `_id` suffix** (e.g., `crop_id`, `plot_id`, `farm_id`, `user_id`, `planted_crop_id`)
- **Values are ALWAYS UUIDs** (string), not integer IDs
- This maintains API consistency - external APIs always use `_id` keys with UUID values
- Examples:
  ```json
  {
    "crop_id": "8d99a668-1863-4f4b-8025-b50e66c48ff5",
    "plot_id": "9edec237-2122-4ae9-af10-de5abe7bdc47",
    "planted_crop_id": "abc123..."
  }
  ```

#### Implementation Pattern
- Routes: Accept `_id` keys from request body, extract UUID values
  ```python
  crop_uuid = data.get('crop_id')  # Key is crop_id, value is UUID
  ```
- Controllers: Accept `_uuid` parameters internally for clarity
  ```python
  async def create_planted_crop(user_uuid: str, data: Dict[str, Any]):
      crop_uuid = data.get("crop_id")  # Extract UUID from _id key
  ```
- Database Operations:
  - Convert UUIDs to IDs internally when needed for database operations
  - Use UUID-based filtering for user queries (e.g., `User.uuid == user_uuid`)
  - Use ID-based foreign key relationships internally (e.g., `PlantedCrop.user_id == user.id`)
- Authentication: User data from token includes both `id` and `uuid` - always pass `user['uuid']` to controllers
- Examples:
  - Request body: `"crop_id": "uuid-value"` → Controller: `crop_uuid = data.get('crop_id')`
  - Filtering: `select(Crop).filter(Crop.uuid == crop_uuid)` (external lookup)
  - Relationships: `PlantedCrop.crop_id = crop.id` (internal FK)

### Caching
- Remember to invalidate the relevant caches when doing crud operations on database objects