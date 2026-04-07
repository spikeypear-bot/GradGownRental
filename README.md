# GradGownRental

A microservices-based graduation gown rental system. Students browse packages, reserve gowns, pay online, receive or collect their order, and return items — with automated notifications, logistics tracking, and inventory maintenance throughout.

---

## Architecture

The system is split into **atomic microservices** (each owns its own database) and **saga orchestrators** (stateless, coordinate across services). All traffic is routed through **Kong API Gateway**.

### Services

| Service | Port | Responsibility |
|---------|------|----------------|
| `inventory-service` | 8080 | Packages, stock levels, soft-holds, state transitions |
| `order-service` | 8081 | Order lifecycle (PENDING → CONFIRMED → ACTIVE → RETURNED → COMPLETED) |
| `payment-service` | 3000 | Stripe PaymentIntents, payment verification, refunds |
| `notification-service` | 5001 | Transactional emails via SendGrid, triggered by Kafka events |
| `logistics-service` | 5004 | Shipment tracking proxy to OutSystems |
| `error-service` | 5002 | Centralized saga failure logging |

### Sagas

| Saga | Port | Responsibility |
|------|------|----------------|
| `place-order-saga` | 5003 | Checkout: create order → payment → reserve inventory |
| `fulfill-order-saga` | 5005 | Fulfillment: activate order → sync logistics → mark inventory RENTED |
| `return-order-saga` | 5006 | Return: assess damage → refund → trigger maintenance |

---

## Key Flows

### Checkout (`place-order-saga`)

1. `POST /orders/create` — creates order and PaymentIntent, returns `client_secret` to frontend
2. Frontend collects card details via Stripe.js and confirms payment
3. `POST /submit-payment` — verifies payment, confirms order, converts soft-hold to hard reservation
4. Publishes `OrderConfirmed` (email receipt) and `OrderPaid` (logistics scheduling) to Kafka

### Fulfillment (`fulfill-order-saga`)

1. `POST /fulfillment/activate` — activates order, syncs OutSystems tracking (COLLECTED or DELIVERED), transitions inventory RESERVED → RENTED
2. Publishes `OrderActivated` to Kafka → student receives handover instructions email

### Return (`return-order-saga`)

1. `POST /returns/process` — partitions items into clean/damaged, updates order status, calculates refund, triggers maintenance
2. Clean items: RENTED → WASH → AVAILABLE
3. Damaged items: RENTED → DAMAGED → REPAIR → WASH → AVAILABLE
4. Publishes `ReturnProcessed` to Kafka → student receives refund summary email

---

## Inventory State Machine

```
AVAILABLE
  └─ (soft-hold)      → AVAILABLE (hold tracked separately, 10-min expiry)
  └─ (reserved)       → RESERVED
       └─ (fulfilled) → RENTED
            ├─ (clean return)   → WASH → AVAILABLE
            └─ (damaged return) → DAMAGED → REPAIR → WASH → AVAILABLE
```

---

## Kafka Events

| Topic | Publisher | Consumer |
|-------|-----------|----------|
| `OrderConfirmed` | place-order-saga | notification-service |
| `OrderPaid` | place-order-saga | logistics-service |
| `OrderActivated` | fulfill-order-saga | notification-service |
| `ReturnProcessed` | return-order-saga | notification-service |
| `pickup_reminder` | order-service (scheduler) | notification-service |
| `return_reminder` | order-service (scheduler) | notification-service |

---

## Project Structure

```
GradGownRental/
├── docker-compose.yml
├── .env.example
├── kong/
│   └── kong.yml                   ← Kong route config
├── services/
│   ├── error-service/
│   ├── inventory-service/         ← Java/Spring Boot
│   ├── logistics-service/
│   ├── notification-service/
│   ├── order-service/
│   └── payment-service/
└── sagas/
    ├── place-order-saga/
    ├── fulfill-order-saga/
    └── return-order-saga/
```

Each service contains a `Dockerfile`, source code, and a `db/` folder with SQL init scripts where applicable.

---

## Setup

### 1. Clone and configure environment

```bash
git clone <repo-url>
cd GradGownRental
cp .env.example .env
```

Fill in the required values in `.env`:

| Variable | Description |
|----------|-------------|
| `STRIPE_SECRET_KEY` | Stripe secret key |
| `STRIPE_ENDPOINT_SECRET` | Stripe webhook signing secret |
| `VITE_STRIPE_PUBLISHABLE_KEY` | Stripe publishable key (frontend) |
| `SENDGRID_API_KEY` | SendGrid API key |
| `SENDGRID_FROM_EMAIL` | Verified sender email |
| `VITE_API_BASE_URL` | API base URL (default: `http://localhost:8000`) |

DB passwords and Kafka settings have sensible defaults in `.env.example` and can be left as-is for local development.

### 2. Start all services

```bash
docker compose up --build -d
```

This starts all microservices, sagas, Kafka, PostgreSQL databases, and Kong. Databases and Kong are initialised and configured automatically on startup.

### 3. Access the app

| URL | Description |
|-----|-------------|
| `http://localhost:5173` | Frontend (Vue app) |
| `http://localhost:8000` | Kong proxy (API gateway) |
| `http://localhost:8001` | Kong Admin API |
| `http://localhost:8002` | Kong Admin GUI |

## API Docs

Swagger/OpenAPI docs are available per service after startup. See `docs/SWAGGER_DOCS.md` for the full list of `/docs` URLs.
