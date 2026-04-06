# Kong API Gateway Setup

## Overview
Kong is an API Gateway that sits in front of all your microservices, providing a single entry point for all API requests.

## How It Works

### Architecture
```
Frontend/Client
    ↓
Kong Proxy (8000) ← Public API Entry Point
    ↓
Routes to appropriate service based on path
    ↓
Microservices (Order, Inventory, Payment, etc.)
```

### Key Ports
- **8000**: Kong Proxy (Main API endpoint - this is what you call)
- **8001**: Kong Admin API (for configuration)
- **8002**: Kong GUI (visual interface at http://localhost:8002)

## Services Configured in Kong

### 1. **Error Service** (port 5002)
- Health check: `GET /error-service/health` → `/health`
- Routes:
  - `GET /errors`
  - `POST /errors`

### 2. **Logistics Service** (port 5004)
- Health check: `GET /logistics-service/health`
- Routes:
  - `GET /logistics/{shipment_id}`
  - `POST /logistics/events/order-paid`
  - `PUT /logistics/{shipment_id}/status`

### 3. **Notification Service** (port 5001)
- Health check: `GET /notification-service/health`
- Routes:
  - `GET /notifications/{order_id}`

### 4. **Order Service** (port 8081)
- Health check: `GET /order-service/health` → `/health`
- Routes:
  - `GET /orders/status/{status}`
  - `GET /orders/by-email/{email}`
  - `GET /orders/{order_id}`
  - `POST /orders`
  - `PUT /orders/{order_id}/status`

### 5. **Payment Service** (port 3000)
- Routes:
  - `GET /api/payment/health`
  - `POST /api/payment/checkout`
  - `POST /api/payment/payments`
  - `POST /api/payment/webhook`

### 6. **Inventory Service** (port 8080)
- Health check: `GET /inventory-service/health` → `/health`
- Routes:
  - `GET /api/inventory/availability90`
  - `GET /api/inventory/availability`
  - `GET /api/inventory/catalogue`
  - `POST /api/inventory/soft-hold`
  - `PUT /api/inventory/stock/transition`
  - `PUT /api/inventory/maintenance/request`
  - `GET /api/inventory/packages/all`
  - `GET /api/inventory/packages`
  - `GET /api/inventory/stock-overview`
  - `GET /api/inventory/{packageid}`

### 7. **Place Order Saga** (port 5003)
- Health check: `GET /place-order-saga/health` → `/health`
- Routes:
  - `POST /orders/create`
  - `POST /submit-payment`

### 8. **Fulfill Order Saga** (port 5004)
- Health check: `GET /fulfill-order-saga/health` → `/health`
- Routes:
  - `POST /fulfillment/activate`

### 9. **Return Order Saga** (port 5005)
- Health check: `GET /return-order-saga/health` → `/health`
- Routes:
  - `POST /returns/process`
  - `PUT /returns/transition-to-wash`
  - `PUT /returns/maintenance-complete`

## Docker Compose Services

### Kong Components:
1. **kong-db**: PostgreSQL database for Kong configuration
   - Persists routes, services, and credentials
   
2. **kong-migrations**: Initializes Kong database schema
   - Runs once during setup
   
3. **kong**: The actual API Gateway
   - Listens on 8000, 8001, 8002
   - Routes requests to backend services
   
4. **kong-config**: Deck tool that syncs the `kong.yml` file to Kong
   - Watches `/kong/kong.yml`
   - Automatically applies changes to Kong

## Configuration File

**Location**: `/kong/kong.yml`

This is a declarative configuration file that defines:
- All services and their URLs
- All routes and their paths
- Path stripping rules (e.g., `/api/payment/health` strips the prefix)

## Key Features

### 1. **Path Stripping**
```yaml
strip_path: true   # /error-service/health → /health (upstream)
strip_path: false  # /orders stays /orders
```

### 2. **Regex Routes**
```yaml
paths: ["~/api/inventory/(?<packageid>[^#?/]+)$"]
# Matches: /api/inventory/12345
```

### 3. **Multiple HTTP Methods**
```yaml
methods: [GET, POST, PUT, DELETE, OPTIONS]
```

### 4. **Load Balancing**
Kong automatically load-balances across multiple upstream services if configured

## How to Use

### Making API Calls

**Via Kong (Recommended)**:
```bash
curl http://localhost:8000/orders/status/CONFIRMED
curl http://localhost:8000/api/inventory/catalogue
curl http://localhost:8000/api/payment/checkout
```

**Direct (Bypassing Kong)**:
```bash
curl http://localhost:8081/orders/status/CONFIRMED
curl http://localhost:8080/api/inventory/catalogue
```

### Checking Kong Health
```bash
# Via Kong proxy
curl http://localhost:8000/order-service/health

# Via Kong Admin API
curl http://localhost:8001/status

# Via Kong GUI
open http://localhost:8002
```

## Benefits

1. **Single Entry Point**: All APIs through one URL
2. **Centralized Configuration**: Manage all routes in one file
3. **Security**: Can add authentication, rate limiting, etc.
4. **Monitoring**: Built-in logging and metrics
5. **Load Balancing**: Distribute traffic across services
6. **API Versioning**: Easy to version APIs without changing backend

## Troubleshooting

### Kong not starting?
```bash
# Check docker logs
docker logs kong
docker logs kong-config
docker logs kong-migrations
```

### Routes not working?
1. Check Kong Admin API: `curl http://localhost:8001/services`
2. Check Kong config file: `/kong/kong.yml`
3. Ensure backend service is running on correct port
4. Check Kong logs: `docker logs kong`

### Making changes to routes?
1. Edit `/kong/kong.yml`
2. kong-config automatically syncs changes
3. Verify with: `curl http://localhost:8001/services`

## Frontend Integration

In `frontend/.env.example`:
```
VITE_API_BASE_URL=http://localhost:8000
```

Frontend calls should go through Kong proxy port 8000, not individual service ports.
