# SETTING UP THE SERVICE

Run in the root terminal where the yaml file lies in

`docker compose up --build `

inventory-service-db -> port 1234:5432
inventory-service -> 8080:8080

To view the databases, run in the terminal 

`docker exec -it my-postgres psql -U postgres`

`SET search_path TO inventory_service;`
`select * from inventory limit 5;` 




# TESTING THE SERVICE

The main supported flows are below.

### 1. Finding Package by PackageId

GET

http://localhost:8080/api/inventory/{packageId}

Returns the package together with the model IDs and sizes for each item in the package.

### 2. Getting availability of Hood, Gown, Hat on a given date

GET

http://localhost:8080/api/inventory/availability?hatModelId=0000024&hoodModelId=0000002&gownModelId=0100020&date=2026-03-15

Returns the total available qty of the set and the available qty of each component.

### 3. Getting availability for the next 90 days

GET

http://localhost:8080/api/inventory/availability90?hatModelId=0000024&hoodModelId=0000002&gownModelId=0100020

Returns the availability for the next 90 days starting from the request date.

### 4. Get all packages and pricing

GET

http://localhost:8080/api/inventory/catalogue

### 5. Filter packages by institution, level, or faculty

GET

http://localhost:8080/api/inventory/catalogue?institution=NUS

### 6. Soft-hold items

POST

http://localhost:8080/api/inventory/soft-hold

Body:

```json
[
  {
    "modelId": "0000024",
    "qty": 1,
    "chosenDate": "2026-03-15"
  },
  {
    "modelId": "0000002",
    "qty": 1,
    "chosenDate": "2026-03-15"
  },
  {
    "modelId": "0100020",
    "qty": 1,
    "chosenDate": "2026-03-15"
  }
]
```

Notes:
- returns a generated `holdId`
- soft-holds only remain valid for 10 minutes
- soft-holds are date-aware and only block the relevant 7-day rental window for the given `chosenDate`

### 7. Reserve items after payment

POST

http://localhost:8080/api/inventory/reserveitems

Body:

```json
{
  "holdId": "35b7d04a-47ad-4cd7-ab9a-fde986a22ead",
  "items": [
    {
      "modelId": "0000024",
      "qty": 1,
      "chosenDate": "2026-03-15"
    },
    {
      "modelId": "0000002",
      "qty": 1,
      "chosenDate": "2026-03-15"
    },
    {
      "modelId": "0100020",
      "qty": 1,
      "chosenDate": "2026-03-15"
    }
  ]
}
```

This moves inventory from available to reserved for the 7-day rental window.

### 8. Generic stock transition endpoint

PUT

http://localhost:8080/api/inventory/stock/transition

Body:

```json
{
  "transition": "RESERVED_TO_RENTED",
  "items": [
    {
      "modelId": "0000024",
      "qty": 1,
      "chosenDate": "2026-03-15"
    },
    {
      "modelId": "0000002",
      "qty": 1,
      "chosenDate": "2026-03-15"
    },
    {
      "modelId": "0100020",
      "qty": 1,
      "chosenDate": "2026-03-15"
    }
  ]
}
```

Supported transitions:
- `AVAILABLE_TO_RESERVED`
- `RESERVED_TO_RENTED`
- `RENTED_TO_WASH`
- `RENTED_TO_DAMAGED`
- `DAMAGED_TO_REPAIR`
- `REPAIR_TO_WASH`
- `WASH_TO_AVAILABLE`

Transition behavior:
- `AVAILABLE_TO_RESERVED`: reserve stock using holdId plus items
- `RESERVED_TO_RENTED`: staff handover completed, reserved stock becomes rented
- `RENTED_TO_WASH`: returned clean items move from rented to wash for the remaining booking window
- `RENTED_TO_DAMAGED`: returned damaged items move from rented to damaged
- `DAMAGED_TO_REPAIR`: damaged items move from damaged to repair
- `REPAIR_TO_WASH`: repaired items move from repair to wash
- `WASH_TO_AVAILABLE`: washed items leave wash and become available again

### 9. Checking stock overview

GET

http://localhost:8080/api/inventory/stock-overview?date=2026-03-15

Returns per-model counts for:
- available
- reserved
- rented
- damaged
- repair
- wash
- backup

### 10. Verifying inventory movement in PostgreSQL

Run:

```sql
SET search_path TO inventory_service;

SELECT date, model_id, reserved_qty, rented_qty, damaged_qty, repair_qty, wash_qty, backup_qty
FROM inventoryquantitytrack
WHERE model_id IN ('0000024', '0000002', '0100020')
ORDER BY date DESC, model_id;
```

This is the easiest way to verify that transitions are updating the expected quantity buckets.


# Structures of the service

Entities -> Repository -> Service -> Controller (Entrypoint for API)

Entities: GraduationPackage, Inventory , Inventory Style, ItemHold 

Repository: ^^

Service: ^^ + PostService + GetService

Controller: InventoryController

### More features like exceptions and response or request bodies to be added.



## Entities
### 1. InventoryStyle
Refers to the different styles, example like Blue Gown, or Crimson Edge Hood, these two would be different style. All styles have same rental fee and deposit and is defined in this entity. 

### 2. Inventory
Entity keeping track of the total quantities per model, as well as the size of it. 
Two sets of clothings are considered different model, if they have different styles (Mapped by style id), and different sizes
Example: M Blue Gown and S Blue gown is different model, but two of the S blue gown are considered the same model id.

### 3. InventoryQuantityTrack
Tracks quantity of inventory day by day for each model.
Quantities are tracked as:
- reserved
- rented
- damaged
- repair
- wash
- backup

The rental window is treated as a 7-day blocked period beginning from `chosenDate`.
Operational transitions move qty between these buckets as the order progresses through fulfillment, return, repair, and washing.

### 4. GraduationPackage
The Grad package mainly defines the type of packages offered, in particular the different packages maps to different faculty, institution and education level.
Students are only allow to buy packages. 

### 5. ItemHold
Used for soft holding of items before payment is completed.
Each hold stores:
- `holdId`
- `modelId`
- `qty`
- `chosenDate`
- `createdAt`

Item holds:
- expire after 10 minutes
- are purged automatically when hold data is accessed
- only affect availability for the matching rental window derived from `chosenDate`

## Repositories

It defines function to allow the service classes to make uses of the entity, defines function to make queries on the tables of the database. 

## Service

Main crux of business logic. Consists of services for each entity, as well as a post service and a get service.

## Controller 
Post mapping and get mapping to connect and receive api calls

## 







