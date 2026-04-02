import logging
import os
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)
    app.extensions["error_logs"] = []

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "error-service"}), 200

    @app.post("/errors")
    def log_error():
        body = request.get_json() or {}
        required = ["saga", "step", "detail"]
        missing = [f for f in required if f not in body]
        if missing:
            return jsonify({"error": f"Missing required fields: {missing}"}), 400

        record = {
            "saga": body["saga"],
            "step": body["step"],
            "order_id": body.get("order_id"),
            "detail": body["detail"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        app.extensions["error_logs"].append(record)
        logger.error(
            "[%s] %s failed | order_id=%s | %s",
            record["saga"],
            record["step"],
            record["order_id"],
            record["detail"],
        )
        return jsonify({"logged": True}), 201

    @app.get("/errors")
    def list_errors():
        return jsonify(app.extensions["error_logs"]), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5002)), debug=False)
