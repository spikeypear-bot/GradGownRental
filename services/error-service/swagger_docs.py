from flask import Response, jsonify


ERROR_OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Error Service API",
        "version": "1.0.0",
        "description": "Capture and inspect saga error events.",
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
                                "example": {"status": "ok", "service": "error-service"}
                            }
                        },
                    }
                },
            }
        },
        "/health/db": {
            "get": {
                "summary": "Database health check",
                "responses": {
                    "200": {
                        "description": "Database is reachable",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/HealthDbResponse"}
                            }
                        },
                    },
                    "500": {"description": "Database is unavailable"},
                },
            }
        },
        "/errors": {
            "get": {
                "summary": "List captured errors",
                "responses": {
                    "200": {
                        "description": "Error log entries",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/ErrorLog"},
                                }
                            }
                        },
                    }
                },
            },
            "post": {
                "summary": "Record a saga error",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/CreateErrorRequest"}
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "Error recorded",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CreateErrorResponse"}
                            }
                        },
                    },
                    "400": {"description": "Missing required fields"},
                },
            },
        },
        "/errors/{error_id}": {
            "get": {
                "summary": "Get a captured error by ID",
                "parameters": [
                    {
                        "name": "error_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Error log entry",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorLog"}
                            }
                        },
                    },
                    "404": {"description": "Error not found"},
                },
            }
        },
    },
    "components": {
        "schemas": {
            "CreateErrorRequest": {
                "oneOf": [
                    {
                        "type": "object",
                        "properties": {
                            "saga": {"type": "string"},
                            "step": {"type": "string"},
                            "order_id": {"type": "string"},
                            "detail": {"type": "string"},
                            "status_code": {"type": "integer"},
                        },
                        "required": ["saga", "step", "detail"],
                    },
                    {
                        "type": "object",
                        "properties": {
                            "saga_name": {"type": "string"},
                            "step": {"type": "string"},
                            "order_id": {"type": "string"},
                            "error_message": {"type": "string"},
                            "status_code": {"type": "integer"},
                        },
                        "required": ["saga_name", "step", "error_message"],
                    },
                ]
            },
            "CreateErrorResponse": {
                "type": "object",
                "properties": {
                    "error_id": {"type": "string"},
                    "status": {"type": "string", "example": "logged"},
                },
                "required": ["error_id", "status"],
            },
            "ErrorLog": {
                "type": "object",
                "properties": {
                    "error_id": {"type": "string"},
                    "saga_name": {"type": "string"},
                    "step": {"type": "string"},
                    "order_id": {"type": "string"},
                    "error_message": {"type": "string"},
                    "status_code": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"},
                },
            },
            "HealthDbResponse": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "service": {"type": "string"},
                    "records": {"type": "integer"},
                },
                "required": ["status", "service", "records"],
            },
        }
    },
}


def register_swagger(app) -> None:
    @app.get("/openapi.json")
    def openapi_spec():
        return jsonify(ERROR_OPENAPI_SPEC)

    @app.get("/docs")
    def swagger_ui():
        return Response(
            """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Error Service Docs</title>
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
