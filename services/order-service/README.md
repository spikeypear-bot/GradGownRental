# Order Service

Manages order lifecycle: creation, activation, returns, and damage tracking with deposit validation and automatic fulfillment processing.

## Overview

**Order Lifecycle:**
```
CONFIRMED → ACTIVE → RETURNED → COMPLETED
```

- **CONFIRMED**: Payment processed, order ready for pickup/delivery
- **ACTIVE**: Rental period started (student has rented the items)
- **RETURNED**: Items returned by student to store
- **COMPLETED**: Return processed and finalized

**Key Features:**
- ✅ Deposit tracking from selected items
- ✅ 24-hour minimum validation for DELIVERY fulfillment
- ✅ Same-day COLLECTION orders for walk-in rentals
- ✅ Automatic DELIVERY activation on rental_start_date
- ✅ Damage tracking with item-level detail (modelId, qty)
- ✅ Damage validation ensures reported damage doesn't exceed selected items
- ✅ No delivery_fee stored (frontend calculates $5 if DELIVERY selected)

---

## Current Implementation Notes

- Orders may begin as `PENDING` before payment confirmation in the full checkout flow.
- Returned orders now move to `RETURNED` or `RETURNED_DAMAGED` first.
- Orders only move to `COMPLETED` after the return maintenance flow finishes.
- DELIVERY now requires `rental_start_date` to be after today.
- Same-day delivery is rejected, while same-day collection is still allowed.

## Business Rules

### Fulfillment Method Validation

**DELIVERY Orders:**
- `rental_start_date` must be **at least 24 hours in the future**
- Ensures adequate time for logistics planning
- Same-day deliveries are NOT permitted
- Auto-activated on rental_start_date at 6 AM via scheduled job

**COLLECTION Orders:**
- No time restriction on `rental_start_date`
- Enables same-day pickups for walk-in orders
- Must be manually activated by staff when student arrives
- No automatic activation

### Damage Validation

When marking an order as returned with damaged items:
- Each damaged item's `modelId` must exist in the order's `selected_items`
- Damaged qty for each item cannot exceed the selected qty for that item
- Examples:
  - ✅ Order has `hat: 1`, damage report: `hat: 1` → Valid
  - ✅ Order has `gown: 2`, damage report: `gown: 1` → Valid
  - ❌ Order has `hat: 1`, damage report: `hat: 2` → Invalid (exceeds selected qty)
  - ❌ Order has `gown: 1`, damage report: `jacket: 1` → Invalid (not in order)

---

## API Endpoints

### 1. Health Check
**GET** `/health`

Check if the service is running.

**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "order-service"
}
```

---

### 2. Create Order
**POST** `/orders`

Creates a new order in CONFIRMED state.

In the end-to-end checkout flow, orders are typically created in `PENDING` and later confirmed by the payment/saga path.

**Request Body:**
```json
{
  "order_id": "ORD-001",
  "student_name": "Alice Chen",
  "email": "alice@example.com",
  "phone": "+65-1234-5678",
  "package_id": 5,
  "selected_items": [
    {"modelId": "0000024", "qty": 1},
    {"modelId": "0000002", "qty": 1},
    {"modelId": "0100020", "qty": 1}
  ],
  "rental_start_date": "2026-05-15",
  "rental_end_date": "2026-05-18",
  "total_amount": 75.00,
  "deposit": 75.00,
  "fulfillment_method": "DELIVERY"
}
```

**Field Explanations:**
- `order_id`: Unique order identifier
- `student_name`, `email`, `phone`: Student contact information
- `package_id`: Graduation package selected (e.g., 1=NUS, 5=SMU)
- `selected_items`: Array of items with modelId and quantity
- `total_amount`: Total charged to student (includes $5 delivery fee if DELIVERY selected)
- `deposit`: Total deposit amount from all items
- `fulfillment_method`: "COLLECTION" or "DELIVERY"

**Validation:**
- DELIVERY orders with same-day `rental_start_date` will be rejected with 400 error
- COLLECTION orders can have same-day dates

Current validation message:
- `DELIVERY orders require rental_start_date after today. For same-day rentals, please use COLLECTION fulfillment method.`

**Response (201 Created):**
```json
{
  "order_id": "ORD-001",
  "student_name": "Alice Chen",
  "email": "alice@example.com",
  "phone": "+65-1234-5678",
  "package_id": 5,
  "selected_items": [...],
  "rental_start_date": "2026-05-15",
  "rental_end_date": "2026-05-18",
  "total_amount": 75.00,
  "deposit": 75.00,
  "fulfillment_method": "DELIVERY",
  "status": "CONFIRMED",
  "damaged": false,
  "damaged_items": [],
  "confirmed_at": "2026-03-22T14:30:00",
  "created_at": "2026-03-22T14:30:00",
  "updated_at": "2026-03-22T14:30:00",
  ...
}
```

**Error (400):**
```json
{
  "error": "DELIVERY orders require rental_start_date to be at least 24 hours in the future. For same-day rentals, please use COLLECTION fulfillment method."
}
```

---

### 3. Get Order by ID
**GET** `/orders/<order_id>`

Fetch a specific order by its order_id.

**Example Request:**
```bash
GET /orders/ORD-001
```

**Response (200 OK):**
```json
{
  "order_id": "ORD-001",
  "status": "ACTIVE",
  "damaged": true,
  "damaged_items": [
    {"modelId": "0100020", "qty": 1}
  ],
  ...
}
```

**Error (404):**
```json
{
  "error": "Order ORD-999 not found"
}
```

---

### 4. Get Orders by Email
**GET** `/orders/by-email/<email>`

Fetch all orders for a student by email address.

**Example Request:**
```bash
GET /orders/by-email/alice@example.com
```

**Response (200 OK):**
```json
[
  {
    "order_id": "ORD-001",
    "status": "COMPLETED",
    ...
  },
  {
    "order_id": "ORD-002",
    "status": "ACTIVE",
    ...
  }
]
```

---

### 5. Get Orders by Status
**GET** `/orders/status/<status>`

Fetch all orders with a specific status (CONFIRMED, ACTIVE, RETURNED, or COMPLETED).

Supported statuses now also include `PENDING` and `RETURNED_DAMAGED`.

**Example Request:**
```bash
GET /orders/status/CONFIRMED
```

**Response (200 OK):**
```json
[
  {
    "order_id": "ORD-001",
    ...
  },
  {
    "order_id": "ORD-002",
    ...
  }
]
```

**Error (400):**
```json
{
  "error": "Invalid status: INVALID_STATUS"
}
```

---

### 6. Activate Order
**POST** `/orders/<order_id>/activate`

Mark order as ACTIVE (rental period started).

**Usage:**
- **COLLECTION**: Staff manually calls this when student picks up
- **DELIVERY**: Auto-activated by scheduled job on rental_start_date (no manual action needed)

**Example Request:**
```bash
POST /orders/ORD-001/activate
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "order_id": "ORD-001",
  "status": "ACTIVE",
  "activated_at": "2026-03-22T14:00:00",
  ...
}
```

**Error (400):**
```json
{
  "error": "Cannot activate order in COMPLETED state"
}
```

---

### 7. Mark Order as Returned
**POST** `/orders/<order_id>/return`

Mark order as returned (gown received back).

This endpoint now sets the order to `RETURNED` or `RETURNED_DAMAGED`. Final `COMPLETED` closure happens later when the return maintenance flow confirms the items are cleared.

**Request Body:**
```json
{
  "damaged_items": [
    {"modelId": "0100020", "qty": 1}
  ]
}
```

**Field Explanations:**
- `damaged_items`: Array of damaged items (empty array if no damage)
  - Each item must have `modelId` and `qty`
  - `modelId` must exist in the order's `selected_items`
  - `qty` cannot exceed the selected quantity for that item

**Validation:**
- Only orders in ACTIVE state can be marked as returned
- Damaged items are validated against selected items
- Qty cannot exceed selected qty (400 error if validation fails)

**Response (200 OK):**
```json
{
  "order_id": "ORD-001",
  "status": "COMPLETED",
  "damaged": true,
  "damaged_items": [
    {"modelId": "0100020", "qty": 1}
  ],
  "returned_at": "2026-03-25T10:00:00",
  "completed_at": "2026-03-25T10:00:00",
  ...
}
```

**Error Examples:**

Not found (404):
```json
{
  "error": "Order ORD-999 not found"
}
```

Invalid state (400):
```json
{
  "error": "Cannot return order in CONFIRMED state"
}
```

Damage exceeds selected (400):
```json
{
  "error": "Damaged qty (3) for modelId '0100020' exceeds selected qty (1)"
}
```

Item not in order (400):
```json
{
  "error": "Damaged item with modelId 'INVALID' was not part of this order"
}
```

---

## Database Schema

### Orders Table

| Column | Type | Notes |
|--------|------|-------|
| `id` | SERIAL PRIMARY KEY | Database internal ID |
| `order_id` | VARCHAR(255) UNIQUE NOT NULL | Unique order identifier |
| `student_name` | VARCHAR(255) NOT NULL | Student's full name |
| `email` | VARCHAR(255) NOT NULL | Student's email |
| `phone` | VARCHAR(20) NOT NULL | Student's phone number |
| `package_id` | INT NOT NULL | Graduation package ID |
| `selected_items` | JSONB NOT NULL | Selected items with quantities |
| `rental_start_date` | DATE NOT NULL | Rental start date |
| `rental_end_date` | DATE NOT NULL | Rental end date |
| `total_amount` | DECIMAL(10, 2) NOT NULL | Total amount charged |
| `deposit` | DECIMAL(10, 2) | Total deposit from items |
| `fulfillment_method` | VARCHAR(50) NOT NULL | COLLECTION or DELIVERY |
| `status` | VARCHAR(50) NOT NULL | CONFIRMED, ACTIVE, RETURNED, COMPLETED |
| `damaged` | BOOLEAN | Whether items were damaged |
| `damaged_items` | JSONB | List of damaged items with quantities |
| `confirmed_at` | TIMESTAMP NOT NULL | When order was confirmed |
| `activated_at` | TIMESTAMP | When order was activated |
| `returned_at` | TIMESTAMP | When items were returned |
| `completed_at` | TIMESTAMP | When order was completed |
| `created_at` | TIMESTAMP NOT NULL | Record creation timestamp |
| `updated_at` | TIMESTAMP NOT NULL | Record update timestamp |
| `hold_id` | VARCHAR(255) | Reference to Inventory Service hold |
| `payment_id` | VARCHAR(255) | Reference to Payment Service |

---

## Environment Variables

```bash
DB_HOST=localhost          # PostgreSQL host
DB_PORT=5432              # PostgreSQL port
DB_NAME=order             # Database name
DB_USER=order_user        # Database user
DB_PASSWORD=order_pass    # Database password
FLASK_ENV=development     # Flask environment
```

---

## Running the Service

### Using Docker Compose

```bash
cd /path/to/GradGownRental
docker-compose up -d order-service
```

### Manual Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables and run:
   ```bash
   export DB_HOST=localhost
   export DB_PORT=5432
   export DB_NAME=order
   export DB_USER=order_user
   export DB_PASSWORD=order_pass
   
   python -m src.app
   ```

Service will be available at `http://localhost:8081`

---

## Key Implementation Details

### Delivery Fee Calculation
- Frontend adds a **flat $5 delivery fee** if fulfillment_method is "DELIVERY"
- This fee is **included in the total_amount** sent to the backend
- Backend does NOT calculate delivery fees (kept simple for order service)
- `delivery_fee` field is NOT stored in the database

### Damage Tracking
- Damages are tracked at the **item level** (modelId, qty)
- Inventory service can query damaged orders to know which items need repairs
- `damaged` boolean flag indicates if any damage occurred
- `damaged_items` list contains specific items and quantities damaged

### Order Activation
- **COLLECTION**: Requires manual staff action via `/activate` endpoint
- **DELIVERY**: Automatically activated at 6 AM on rental_start_date by scheduler job

### Validation Strategy
- 24-hour rule enforced for DELIVERY orders at creation time
- Damage validation enforced at return time
- Damaged quantities cannot exceed selected quantities

---

## Testing

Postman collection available at `postman_collection.json` with example requests for:
- Creating COLLECTION orders (same-day)
- Creating DELIVERY orders (future date only)
- Creating DELIVERY orders with same-day dates (shows validation error)
- Getting orders by ID, email, and status
- Activating orders
- Marking orders as returned with/without damage

---

## Service Dependencies

- **PostgreSQL**: Order data persistence
- **APScheduler**: Daily job to activate DELIVERY orders
- **Flask**: REST API framework
- **psycopg2**: PostgreSQL client library

---

## Future Enhancements

- [ ] Pagination for large result sets
- [ ] Soft deletes for orders
- [ ] Order history/audit trail
- [ ] Batch operations
- [ ] Advanced search filters
- [ ] WebSocket support for real-time order updates
