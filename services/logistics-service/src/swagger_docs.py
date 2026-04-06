from flask import Response, jsonify


LOGISTICS_OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Logistics Service API",
        "version": "1.0.0",
        "description": "Kafka-to-OutSystems adapter for gown fulfillment logistics.",
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
                "summary": "Deprecated local HTTP wrapper",
                "description": "Order-paid ingress now comes from Kafka rather than direct HTTP.",
                "responses": {
                    "410": {"description": "Ingress moved to Kafka consumer"},
                },
            }
        },
        "/logistics/{shipment_id}/status": {
            "put": {
                "summary": "Proxy shipment status update to OutSystems",
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
                        "description": "OutSystems shipment updated",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        },
                    },
                    "400": {"description": "Invalid status or shipment_id"},
                    "502": {"description": "Failed to reach OutSystems"},
                },
            }
        },
        "/logistics/order/{order_id}": {
            "get": {
                "summary": "Fetch full shipment by order ID",
                "parameters": [
                    {
                        "name": "order_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Shipment found in OutSystems",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        },
                    },
                    "404": {"description": "Shipment not found for order"},
                    "502": {"description": "Failed to reach OutSystems"},
                },
            }
        },
        "/logistics/order/{order_id}/shipment-id": {
            "get": {
                "summary": "Resolve shipment ID by order ID",
                "parameters": [
                    {
                        "name": "order_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Shipment ID resolved",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "order_id": {"type": "string"},
                                        "shipment_id": {"type": "string"},
                                        "source": {
                                            "type": "string",
                                            "enum": ["outsystems", "cache"],
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "404": {"description": "Shipment not found for order"},
                    "502": {"description": "Failed to reach OutSystems"},
                },
            }
        },
    },
    "components": {
        "schemas": {
            "UpdateShipmentStatusRequest": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "tracking_status": {
                        "type": "string",
                        "enum": ["SCHEDULED", "COLLECTED", "DELIVERED"],
                    },
                },
                "required": ["tracking_status"],
            }
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
