from flask import Response, jsonify


PAYMENT_OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Payment Service API",
        "version": "1.0.0",
        "description": "Checkout, payment authorisation, refund, and Stripe webhook endpoints.",
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
                                "example": {"status": "ok", "service": "payment-service"}
                            }
                        },
                    }
                },
            }
        },
        "/checkout": {
            "post": {
                "summary": "Create a Stripe payment intent",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CheckoutRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Client secret returned"},
                    "500": {"description": "Internal server error"},
                },
            }
        },
        "/payments": {
            "post": {
                "summary": "Authorise or verify a payment",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/AuthorisePaymentRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Existing idempotent payment returned"},
                    "201": {"description": "Payment authorised"},
                    "400": {"description": "Missing fields"},
                    "402": {"description": "Payment failed"},
                },
            }
        },
        "/payments/refunds": {
            "post": {
                "summary": "Refund an authorised payment",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/RefundRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {"description": "No refund needed"},
                    "201": {"description": "Refund created"},
                    "202": {"description": "Simulated refund generated"},
                    "400": {"description": "Invalid refund request"},
                    "402": {"description": "Refund failed"},
                    "404": {"description": "Payment not found"},
                },
            }
        },
        "/webhook": {
            "post": {
                "summary": "Handle Stripe webhook events",
                "responses": {
                    "200": {"description": "Webhook accepted"},
                    "400": {"description": "Invalid payload or signature"},
                },
            }
        },
        "/test": {
            "get": {
                "summary": "Development-only payment listing endpoint",
                "responses": {
                    "200": {"description": "Payments returned"},
                    "400": {"description": "No payments found"},
                },
            }
        },
    },
    "components": {
        "schemas": {
            "CheckoutRequest": {
                "type": "object",
                "properties": {"amount": {"type": "number"}},
                "required": ["amount"],
            },
            "PaymentDetails": {
                "type": "object",
                "properties": {
                    "payment_intent_id": {"type": "string"},
                    "test_payment_method_id": {"type": "string"},
                },
            },
            "AuthorisePaymentRequest": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "total_amount": {"type": "number"},
                    "payment_details": {"$ref": "#/components/schemas/PaymentDetails"},
                },
                "required": ["order_id", "total_amount"],
            },
            "RefundRequest": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "payment_id": {"type": "string"},
                    "refundable_amount": {"type": "number"},
                },
                "required": ["order_id", "payment_id", "refundable_amount"],
            },
        }
    },
}


def register_swagger(app) -> None:
    @app.get("/openapi.json")
    def openapi_spec():
        return jsonify(PAYMENT_OPENAPI_SPEC)

    @app.get("/docs")
    def swagger_ui():
        return Response(
            """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Payment Service Docs</title>
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
