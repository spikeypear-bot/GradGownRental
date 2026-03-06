# Grad-Gown-Rental
Repository is a service structure supporting a graduation gown rental website, contains multiple composite/microservices.


---

## Project Structure

project-root/
├─ docker-compose.yml
├─ .env.example
├─ services/
│ ├─ auth-service/
│ │ ├─ Dockerfile
│ │ ├─ src/
│ │ └─ db/init.sql
│ ├─ error-service/
│ │ ├─ Dockerfile
│ │ ├─ src/
│ │ └─ db/init.sql
│ ├─ inventory-service/
│ ├─ logistics-service/
│ ├─ notification-service/
│ ├─ order-service/
│ └─ payment-service/
└─ volumes/


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