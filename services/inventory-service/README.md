# Inventory Service

Manages gown stock, availability, soft-holds, and inventory state transitions for the GradGownRental system.

## Overview

- **Port**: 8080
- **Tech Stack**: Java, Spring Boot, PostgreSQL
- **Database**: `inventory` (schema: `inventory_service`)
- **Role**: Tracks available gown packages (gown + hood + mortarboard sets), manages soft-holds during checkout, and transitions stock through the rental and maintenance workflow.

## Setup

```bash
# Start with Docker Compose (from project root)
docker compose up --build inventory-service

# View the database
docker exec -it inventory-service-db psql -U $INVENTORY_DB_USER -d inventory
```

```sql
SET search_path TO inventory_service;
SELECT * FROM inventory LIMIT 5;
```

Database port mapping: `1234:5432`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/inventory/{packageId}` | Package details with styles and stock |
| `GET` | `/api/inventory/availability` | Daily availability for a specific set |
| `GET` | `/api/inventory/availability90` | Availability for next 90 days |
| `GET` | `/api/inventory/catalogue` | All packages (filterable) |
| `GET` | `/api/inventory/packages/all` | All packages with pricing |
| `GET` | `/api/inventory/packages` | Filtered packages |
| `GET` | `/api/inventory/stock-overview` | Stock counts per model per state |
| `POST` | `/api/inventory/soft-hold` | Create a soft-hold (10-minute expiry) |
| `POST` | `/api/inventory/reserveitems` | Reserve items after payment (uses holdId) |
| `PUT` | `/api/inventory/stock/transition` | Generic stock state transition |

### GET `/api/inventory/availability`

Check availability for a specific set on a date.

**Query Params**: `hatModelId`, `hoodModelId`, `gownModelId`, `date`

```
GET /api/inventory/availability?hatModelId=0000024&hoodModelId=0000002&gownModelId=0100020&date=2026-03-15
```

Returns total available qty for the set plus per-component breakdown.

### GET `/api/inventory/availability90`

Returns availability for the next 90 days from request date.

**Query Params**: `hatModelId`, `hoodModelId`, `gownModelId`

### GET `/api/inventory/catalogue`

Returns all graduation packages. Supports optional filters:

| Filter | Example |
|--------|---------|
| `institution` | `?institution=NUS` |
| `educationLevel` | `?educationLevel=Bachelor` |
| `faculty` | `?faculty=Computing` |

### POST `/api/inventory/soft-hold`

Temporarily reserves items during checkout. Expires after 10 minutes. Date-aware — blocks only the relevant 7-day rental window for the given `chosenDate`.

**Request Body**:
```json
[
  {"modelId": "0000024", "qty": 1, "chosenDate": "2026-03-15"},
  {"modelId": "0000002", "qty": 1, "chosenDate": "2026-03-15"},
  {"modelId": "0100020", "qty": 1, "chosenDate": "2026-03-15"}
]
```

**Response**: `{ "holdId": "35b7d04a-..." }`

### POST `/api/inventory/reserveitems`

Converts a soft-hold to a hard reservation after payment. Moves inventory from available to reserved for the 7-day rental window.

**Request Body**:
```json
{
  "holdId": "35b7d04a-47ad-4cd7-ab9a-fde986a22ead",
  "items": [
    {"modelId": "0000024", "qty": 1, "chosenDate": "2026-03-15"}
  ]
}
```

### PUT `/api/inventory/stock/transition`

Generic endpoint for all stock state transitions.

**Request Body**:
```json
{
  "transition": "RESERVED_TO_RENTED",
  "items": [
    {"modelId": "0000024", "qty": 1, "chosenDate": "2026-03-15"}
  ]
}
```

### GET `/api/inventory/stock-overview`

Returns per-model counts for all stock states. Accepts optional `?date=YYYY-MM-DD`.

Returns: `available`, `reserved`, `rented`, `damaged`, `repair`, `wash`, `backup`

Notes:
- `backup` defaults to `10` units per model as an operational buffer.
- `damaged` is derived from `DamageLog`, not stored on `InventoryQuantityTrack`.

## Stock State Machine

```
AVAILABLE
  └─ RESERVED       (hold confirmed after payment)
       └─ RENTED    (handed over to student)
            ├─ WASH          (clean return → laundry)
            └─ DAMAGED       (damaged return)
                 └─ REPAIR
                      └─ WASH
  WASH
  └─ AVAILABLE      (maintenance complete)
```

| Transition | Trigger |
|------------|---------|
| `AVAILABLE_TO_RESERVED` | Payment confirmed (Place-Order-Saga) |
| `RESERVED_TO_RENTED` | Gown handed over (Fulfill-Order-Saga) |
| `RENTED_TO_WASH` | Clean return (Return-Order-Saga) |
| `RENTED_TO_DAMAGED` | Damaged return (Return-Order-Saga) |
| `DAMAGED_TO_REPAIR` | Damage logged, sent for repair (Return-Order-Saga) |
| `REPAIR_TO_WASH` | Repair complete (Return-Order-Saga) |
| `WASH_TO_AVAILABLE` | Wash complete, back in stock (Return-Order-Saga) |

## Core Entities

| Entity | Description |
|--------|-------------|
| `GraduationPackage` | A package tied to a specific institution, faculty, and education level |
| `InventoryStyle` | A specific style (e.g., Blue Gown) with rental fee and deposit amount |
| `Inventory` | A style + size combination with a unique `modelId` |
| `InventoryQuantityTrack` | Per-day per-model quantity counters: `reserved`, `rented`, `wash`, `backup` |
| `ItemHold` | Soft-hold record with 10-minute TTL and `chosenDate` for rental window scoping |
| `DamageLog` | Records damaged items (`modelId`, `qty`, `date`, `date_repaired`) per order |

## Architecture

```
Controller (InventoryController)
    └─ Service (GetService, PostService, per-entity services)
         └─ Repository (per-entity JPA repositories)
              └─ PostgreSQL (inventory_service schema)
```

## Verifying Inventory in PostgreSQL

```sql
SET search_path TO inventory_service;

-- Check quantity tracks
SELECT date, model_id, reserved_qty, rented_qty, wash_qty, backup_qty
FROM inventoryquantitytrack
WHERE model_id IN ('0000024', '0000002', '0100020')
ORDER BY date DESC, model_id;

-- Check damage logs
SELECT damage_id, model_id, quantity, date, date_repaired
FROM damagelog
WHERE model_id IN ('0000024', '0000002', '0100020')
ORDER BY date DESC, damage_id DESC;
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SPRING_DATASOURCE_URL` | JDBC URL for PostgreSQL |
| `SPRING_DATASOURCE_USERNAME` | Database user |
| `SPRING_DATASOURCE_PASSWORD` | Database password |
| `INVENTORY_DB_USER` | Used for direct psql access via docker exec |
