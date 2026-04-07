import logging
import os

from flask import Flask, jsonify
from flask_cors import CORS

from app import db
from app.models import ErrorLog
from app.routes import bp as error_bp
from config import Config
from swagger_docs import register_swagger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "error-service"}), 200

    @app.get("/health/db")
    def health_db():
        try:
            count = db.session.query(ErrorLog).count()
            return jsonify({"status": "ok", "service": "error-service", "records": count}), 200
        except Exception as exc:  # noqa: BLE001
            logger.exception("Database health check failed: %s", exc)
            return jsonify({"status": "error", "service": "error-service", "error": str(exc)}), 500

    app.register_blueprint(error_bp)

    register_swagger(app)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5002)), debug=False)
