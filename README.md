# Grad-Gown-Rental
Repository is a service structure supporting a graduation gown rental website, contains multiple composite/microservices.


---

## Project Structure
```
project-root/
├─ docker-compose.yml
├─ .env.example
├─ volumes/
├─ services/                          ← atomic microservices (each owns a DB)
│  ├─ auth-service/
│  │  ├─ Dockerfile
│  │  ├─ src/
│  │  │  ├─ model/
│  │  │  ├─ repository/
│  │  │  ├─ service/
│  │  │  └─ controller/
│  │  └─ db/init.sql
│  ├─ error-service/           
│  ├─ inventory-service/       
│  ├─ logistics-service/       
│  ├─ notification-service/    
│  ├─ order-service/          
│  └─ payment-service/       
│
└─ sagas/                             ← composite orchestrators (no DB of their own)
   ├─ place-order-saga/
   │  ├─ Dockerfile
   │  └─ src/
   │     ├─ model/              ← PlaceOrderContext, SagaStatus
   │     ├─ service/            ← orchestrator logic + KafkaPublisher
   │     ├─ controller/         ← POST /orders/create, POST /submit-payment
   │     └─ clients/            ← OrderClient, PaymentClient, InventoryClient, ErrorClient
   ├─ fulfill-order-saga/       
   └─ return-order-saga/       
```

- `services/<service-name>/` – code, Dockerfile, and database scripts for each microservice  
- `db/init.sql` – optional SQL scripts to initialize the database  
- `docker-compose.yml` – orchestrates all services and databases  
- Volumes (e.g., `auth-data`) store database files and persist data across container restarts  

---

## Getting Started

### 1. Clone the repository

```bash
git clone <repo-url>
cd project-root
```

## API Docs

Swagger/OpenAPI docs are available per service after startup.

- See `docs/SWAGGER_DOCS.md` for the full list of `/docs` and raw spec URLs.

## Recent Updates

- Added OpenAPI/Swagger coverage across the active services and sagas for easier local API inspection.
- Refined the admin operations flow in the frontend for fulfillment, returns, repair, laundry, and maintenance queue handling.
- Extended the inventory transition contract so sagas can drive `AVAILABLE_TO_RESERVED`, `RESERVED_TO_RENTED`, `RENTED_TO_WASH`, `RENTED_TO_DAMAGED`, `DAMAGED_TO_REPAIR`, `REPAIR_TO_WASH`, and `WASH_TO_AVAILABLE`.
- Improved return-order saga handling for split clean versus damaged package processing and maintenance progression.
- Updated inventory availability and stock overview behavior so default backup stock is treated as a buffer and damaged quantities come from the damage log.

## Notes

- Inventory schema changes now treat `backup_qty` with a default value of `10`.
- `damaged_qty` and `repair_qty` are no longer stored in `InventoryQuantityTrack`; damaged counts are derived from `DamageLog`.

