from flask import Response, jsonify


ORDER_OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Order Service API",
        "version": "1.0.0",
        "description": "Endpoints for creating, tracking, activating, and returning rental orders.",
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
                                "example": {"status": "ok", "service": "order-service"}
                            }
                        },
                    }
                },
            }
        },
        "/orders": {
            "post": {
                "summary": "Create an order",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CreateOrderRequest"}
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "Order created",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Order"}
                            }
                        },
                    },
                    "400": {"description": "Validation error"},
                    "500": {"description": "Internal server error"},
                },
            }
        },
        "/orders/{order_id}": {
            "get": {
                "summary": "Get an order by ID",
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
                        "description": "Order found",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Order"}
                            }
                        },
                    },
                    "404": {"description": "Order not found"},
                },
            }
        },
        "/orders/{order_id}/status": {
            "put": {
                "summary": "Update an order status",
                "parameters": [
                    {
                        "name": "order_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/UpdateStatusRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Updated order",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Order"}
                            }
                        },
                    },
                    "400": {"description": "Invalid status"},
                    "404": {"description": "Order not found"},
                },
            }
        },
        "/orders/by-email/{email}": {
            "get": {
                "summary": "List orders by student email",
                "parameters": [
                    {
                        "name": "email",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string", "format": "email"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Orders returned",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Order"},
                                }
                            }
                        },
                    }
                },
            }
        },
        "/orders/{order_id}/activate": {
            "post": {
                "summary": "Activate an order",
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
                        "description": "Order activated",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Order"}
                            }
                        },
                    },
                    "400": {"description": "Invalid state transition"},
                },
            }
        },
        "/orders/{order_id}/return": {
            "post": {
                "summary": "Mark an order as returned",
                "parameters": [
                    {
                        "name": "order_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "requestBody": {
                    "required": False,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ReturnOrderRequest"}
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Order returned",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Order"}
                            }
                        },
                    },
                    "400": {"description": "Validation error"},
                    "404": {"description": "Order not found"},
                },
            }
        },
        "/orders/status/{status}": {
            "get": {
                "summary": "List orders by status",
                "parameters": [
                    {
                        "name": "status",
                        "in": "path",
                        "required": True,
                        "schema": {
                            "type": "string",
                            "enum": ["PENDING", "CONFIRMED", "ACTIVE", "RETURNED", "RETURNED_DAMAGED", "COMPLETED"],
                        },
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Orders returned",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Order"},
                                }
                            }
                        },
                    },
                    "400": {"description": "Invalid status"},
                },
            }
        },
    },
    "components": {
        "schemas": {
            "SelectedItem": {
                "type": "object",
                "properties": {
                    "modelId": {"type": "string"},
                    "qty": {"type": "integer"},
                },
                "required": ["modelId", "qty"],
            },
            "CreateOrderRequest": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "student_name": {"type": "string"},
                    "email": {"type": "string", "format": "email"},
                    "phone": {"type": "string"},
                    "package_id": {"type": "integer"},
                    "selected_items": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/SelectedItem"},
                    },
                    "rental_start_date": {"type": "string", "format": "date"},
                    "rental_end_date": {"type": "string", "format": "date"},
                    "total_amount": {"type": "number"},
                    "deposit": {"type": "number"},
                    "hold_id": {"type": "string"},
                    "payment_id": {"type": "string"},
                    "fulfillment_method": {
                        "type": "string",
                        "enum": ["COLLECTION", "DELIVERY"],
                    },
                    "status": {"type": "string"},
                },
                "required": [
                    "student_name",
                    "email",
                    "phone",
                    "selected_items",
                    "rental_start_date",
                    "rental_end_date",
                    "total_amount",
                    "fulfillment_method",
                ],
            },
            "UpdateStatusRequest": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "order_status": {"type": "string"},
                    "payment_id": {"type": "string"},
                },
            },
            "ReturnOrderRequest": {
                "type": "object",
                "properties": {
                    "damaged_items": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/SelectedItem"},
                    }
                },
            },
            "Order": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "student_name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "package_id": {"type": "integer"},
                    "selected_items": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/SelectedItem"},
                    },
                    "rental_start_date": {"type": "string", "format": "date"},
                    "rental_end_date": {"type": "string", "format": "date"},
                    "total_amount": {"type": "number"},
                    "deposit": {"type": "number"},
                    "fulfillment_method": {"type": "string"},
                    "status": {"type": "string"},
                    "damaged": {"type": "boolean"},
                    "damaged_items": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/SelectedItem"},
                    },
                    "payment_id": {"type": "string"},
                    "hold_id": {"type": "string"},
                },
            },
        }
    },
}


def register_swagger(app) -> None:
    @app.get("/openapi.json")
    def openapi_spec():
        return jsonify(ORDER_OPENAPI_SPEC)

    @app.get("/docs")
    def swagger_ui():
        return Response(
            """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Order Service Docs</title>
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
