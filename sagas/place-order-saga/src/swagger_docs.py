from flask import Response, jsonify


PLACE_ORDER_OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Place Order Saga API",
        "version": "1.0.0",
        "description": "Two-phase checkout orchestration for creating an order and finalising payment.",
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
                                "example": {"status": "ok", "service": "place-order-saga"}
                            }
                        },
                    }
                },
            }
        },
        "/orders/create": {
            "post": {
                "summary": "Initialise checkout",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CreateOrderSagaRequest"}
                        }
                    },
                },
                "responses": {
                    "201": {"description": "Pending order created and client secret returned"},
                    "400": {"description": "Missing required fields"},
                    "500": {"description": "Saga step failed"},
                },
            }
        },
        "/submit-payment": {
            "post": {
                "summary": "Verify payment and complete checkout",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SubmitPaymentSagaRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Checkout completed"},
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
                    "size": {"type": "string"},
                    "itemType": {"type": "string"},
                    "itemName": {"type": "string"},
                    "styleId": {"type": "string"},
                    "rentalFee": {"type": "number"},
                    "deposit": {"type": "number"},
                },
                "required": ["modelId", "qty", "chosenDate"],
            },
            "PaymentDetails": {
                "type": "object",
                "properties": {
                    "method": {"type": "string"},
                    "payer_email": {"type": "string", "format": "email"},
                    "payment_intent_id": {"type": "string"},
                    "client_secret": {"type": "string"},
                },
            },
            "CreateOrderSagaRequest": {
                "type": "object",
                "properties": {
                    "hold_id": {"type": "string"},
                    "selected_packages": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/SelectedPackage"},
                    },
                    "fulfillment_method": {
                        "type": "string",
                        "enum": ["COLLECTION", "DELIVERY"],
                    },
                    "student_name": {"type": "string"},
                    "phone": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "fulfillment_date": {"type": "string", "format": "date"},
                    "return_date": {"type": "string", "format": "date"},
                    "total_amount": {"type": "string"},
                    "package_id": {"type": "integer"},
                },
                "required": [
                    "hold_id",
                    "selected_packages",
                    "fulfillment_method",
                    "student_name",
                    "email",
                    "fulfillment_date",
                    "return_date",
                    "total_amount",
                ],
            },
            "SubmitPaymentSagaRequest": {
                "allOf": [
                    {"$ref": "#/components/schemas/CreateOrderSagaRequest"},
                    {
                        "type": "object",
                        "properties": {
                            "order_id": {"type": "string"},
                            "payment_details": {"$ref": "#/components/schemas/PaymentDetails"},
                        },
                        "required": ["order_id", "payment_details"],
                    },
                ]
            },
        }
    },
}


def register_swagger(app) -> None:
    @app.get("/openapi.json")
    def openapi_spec():
        return jsonify(PLACE_ORDER_OPENAPI_SPEC)

    @app.get("/docs")
    def swagger_ui():
        return Response(
            """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Place Order Saga Docs</title>
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
