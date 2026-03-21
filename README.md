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

