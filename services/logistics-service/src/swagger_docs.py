from flask import Response, jsonify


LOGISTICS_OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Logistics Service API",
        "version": "1.0.0",
        "description": "Track shipment creation and status changes for gown fulfillment.",
    },
    "paths": {
        "/health": {
            "get": {
                "summary": "Health check",
                "responses": {
                    "200": {
                        "description": "Service is healthy",
                        "content": {
                            "application/json": {
                                "example": {"status": "ok", "service": "logistics-service"}
                            }
                        },
                    }
                },
            }
        },
        "/logistics/events/order-paid": {
            "post": {
                "summary": "Create a shipment after payment",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/OrderPaidEvent"}
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "Shipment created",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Shipment"}
                            }
                        },
                    },
                    "400": {"description": "Missing order_id"},
                },
            }
        },
        "/logistics/{shipment_id}/status": {
            "put": {
                "summary": "Update shipment status",
                "parameters": [
                    {
                        "name": "shipment_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/UpdateShipmentStatusRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Shipment updated",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Shipment"}
                            }
                        },
                    },
                    "400": {"description": "Invalid status"},
                },
            }
        },
        "/logistics/{shipment_id}": {
            "get": {
                "summary": "Get a shipment by ID",
                "parameters": [
                    {
                        "name": "shipment_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Shipment found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Shipment"}
                            }
                        },
                    },
                    "404": {"description": "Shipment not found"},
                },
            }
        },
    },
    "components": {
        "schemas": {
            "OrderPaidEvent": {
                "type": "object",
                "properties": {
                    "shipment_id": {"type": "string"},
                    "order_id": {"type": "string"},
                    "fulfillment_method": {"type": "string"},
                    "scheduled_datetime": {"type": "string", "format": "date-time"},
                },
                "required": ["order_id"],
            },
            "UpdateShipmentStatusRequest": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "fulfillment_method": {"type": "string"},
                    "scheduled_datetime": {"type": "string", "format": "date-time"},
                    "tracking_status": {
                        "type": "string",
                        "enum": ["SCHEDULED", "COLLECTED", "DELIVERED"],
                    },
                },
                "required": ["tracking_status"],
            },
            "Shipment": {
                "type": "object",
                "properties": {
                    "shipment_id": {"type": "string"},
                    "order_id": {"type": "string"},
                    "fulfillment_method": {"type": "string"},
                    "tracking_status": {"type": "string"},
                    "scheduled_datetime": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"},
                },
            },
        }
    },
}


def register_swagger(app) -> None:
    @app.get("/openapi.json")
    def openapi_spec():
        return jsonify(LOGISTICS_OPENAPI_SPEC)

    @app.get("/docs")
    def swagger_ui():
        return Response(
            """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Logistics Service Docs</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
      window.ui = SwaggerUIBundle({
        url: '/openapi.json',
        dom_id: '#swagger-ui'
      });
    </script>
  </body>
</html>
            """.strip(),
            mimetype="text/html",
        )
