from flask import Response, jsonify


NOTIFICATION_OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Notification Service API",
        "version": "1.0.0",
        "description": "Read notification delivery logs for a given order.",
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
                                "example": {"status": "ok", "service": "notification-service"}
                            }
                        },
                    }
                },
            }
        },
        "/notifications/{order_id}": {
            "get": {
                "summary": "Get notification logs for an order",
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
                        "description": "Notification logs returned",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/NotificationLog"},
                                }
                            }
                        },
                    }
                },
            }
        },
    },
    "components": {
        "schemas": {
            "NotificationLog": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "order_id": {"type": "string"},
                    "channel": {"type": "string"},
                    "recipient": {"type": "string"},
                    "message": {"type": "string"},
                    "status": {"type": "string"},
                    "provider_message_id": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"},
                },
            }
        }
    },
}


def register_swagger(app) -> None:
    @app.get("/openapi.json")
    def openapi_spec():
        return jsonify(NOTIFICATION_OPENAPI_SPEC)

    @app.get("/docs")
    def swagger_ui():
        return Response(
            """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Notification Service Docs</title>
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
