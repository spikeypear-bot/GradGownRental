from flask import Response, jsonify


FULFILL_ORDER_OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Fulfill Order Saga API",
        "version": "1.0.0",
        "description": "Coordinates order activation, logistics updates, and inventory handover.",
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
                                "example": {"status": "ok", "service": "fulfill-order-saga"}
                            }
                        },
                    }
                },
            }
        },
        "/fulfillment/activate": {
            "post": {
                "summary": "Activate order fulfillment handover",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/FulfillmentActivateRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Fulfillment activated"},
                    "400": {"description": "Missing required fields"},
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
                },
            },
            "FulfillmentActivateRequest": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "shipment_id": {"type": "string"},
                    "tracking_status": {
                        "type": "string",
                        "enum": ["COLLECTED", "DELIVERED", "SCHEDULED"],
                    },
                    "chosen_date": {"type": "string", "format": "date"},
                    "selected_packages": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/SelectedPackage"},
                    },
                },
                "required": ["order_id"],
            },
        }
    },
}


def register_swagger(app) -> None:
    @app.get("/openapi.json")
    def openapi_spec():
        return jsonify(FULFILL_ORDER_OPENAPI_SPEC)

    @app.get("/docs")
    def swagger_ui():
        return Response(
            """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Fulfill Order Saga Docs</title>
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
