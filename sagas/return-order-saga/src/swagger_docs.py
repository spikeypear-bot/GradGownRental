from flask import Response, jsonify


RETURN_ORDER_OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Return Order Saga API",
        "version": "1.0.0",
        "description": "Coordinates returns, damage handling, refunds, and stock restoration.",
    },
    "paths": {
        "/health": {
            "get": {
                "summary": "Health check",
                "responses": {
                    "200": {
                        "description": "Saga is healthy",
                        "content": {
                            "application/json": {
                                "example": {"status": "ok", "service": "return-order-saga"}
                            }
                        },
                    }
                },
            }
        },
        "/returns/process": {
            "post": {
                "summary": "Process a return and compute damage/refund flow",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ProcessReturnRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Return processed"},
                    "400": {"description": "Invalid or missing fields"},
                    "500": {"description": "Saga step failed"},
                },
            }
        },
        "/returns/transition-to-wash": {
            "put": {
                "summary": "Move clean returned items into wash flow",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/OrderItemsRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Transitioned to wash"},
                    "400": {"description": "Invalid or missing fields"},
                    "500": {"description": "Saga step failed"},
                },
            }
        },
        "/returns/maintenance-complete": {
            "put": {
                "summary": "Complete maintenance and optionally complete the order",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/MaintenanceCompleteRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Maintenance completed"},
                    "400": {"description": "Invalid or missing fields"},
                    "500": {"description": "Saga step failed"},
                },
            }
        },
    },
    "components": {
        "schemas": {
            "SelectedPackage": {
                "type": "object",
                "properties": {
                    "modelId": {"type": "string"},
                    "qty": {"type": "integer"},
                    "chosenDate": {"type": "string", "format": "date"},
                    "itemType": {"type": "string"},
                    "itemName": {"type": "string"},
                    "deposit": {"type": "number"},
                },
            },
            "OrderItemsRequest": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "chosen_date": {"type": "string", "format": "date"},
                    "selected_packages": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/SelectedPackage"},
                    },
                },
                "required": ["order_id"],
            },
            "ProcessReturnRequest": {
                "allOf": [
                    {"$ref": "#/components/schemas/OrderItemsRequest"},
                    {
                        "type": "object",
                        "properties": {
                            "payment_id": {"type": "string"},
                            "damaged_components": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["mortarboard", "hood", "gown"],
                                },
                            },
                            "damage_fee": {"type": "number"},
                            "damage_report": {"type": "string"},
                            "damage_images": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                    },
                ]
            },
            "MaintenanceCompleteRequest": {
                "allOf": [
                    {"$ref": "#/components/schemas/OrderItemsRequest"},
                    {
                        "type": "object",
                        "properties": {
                            "complete_order": {"type": "boolean"},
                        },
                    },
                ]
            },
        }
    },
}


def register_swagger(app) -> None:
    @app.get("/openapi.json")
    def openapi_spec():
        return jsonify(RETURN_ORDER_OPENAPI_SPEC)

    @app.get("/docs")
    def swagger_ui():
        return Response(
            """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Return Order Saga Docs</title>
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
