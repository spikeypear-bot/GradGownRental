# Swagger Docs

The services in this repo now expose Swagger/OpenAPI docs at a consistent route where possible.

## Service URLs

- `inventory-service`: `http://localhost:8080/docs`
- `order-service`: `http://localhost:8081/docs`
- `payment-service`: `http://localhost:3000/docs`
- `notification-service`: `http://localhost:5001/docs`
- `error-service`: `http://localhost:5002/docs`
- `logistics-service`: `http://localhost:5004/docs`

## Raw OpenAPI Specs

- `inventory-service`: `http://localhost:8080/v3/api-docs`
- `order-service`: `http://localhost:8081/openapi.json`
- `payment-service`: `http://localhost:3000/openapi.json`
- `notification-service`: `http://localhost:5001/openapi.json`
- `error-service`: `http://localhost:5002/openapi.json`
- `logistics-service`: `http://localhost:5004/openapi.json`

## Notes

- `auth-service` was not included because it does not currently expose an HTTP API.
- The Flask services render Swagger UI from a CDN-backed Swagger UI bundle and serve their own OpenAPI JSON locally.
