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
                    "201": {"description": "Error recorded"},
                    "400": {"description": "Missing required fields"},
                },
            },
        },
    },
    "components": {
        "schemas": {
            "CreateErrorRequest": {
                "type": "object",
                "properties": {
                    "saga": {"type": "string"},
                    "step": {"type": "string"},
                    "order_id": {"type": "string"},
                    "detail": {"type": "string"},
                },
                "required": ["saga", "step", "detail"],
            },
            "ErrorLog": {
                "type": "object",
                "properties": {
                    "saga": {"type": "string"},
                    "step": {"type": "string"},
                    "order_id": {"type": "string"},
                    "detail": {"type": "string"},
                    "timestamp_utc": {"type": "string", "format": "date-time"},
                },
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
