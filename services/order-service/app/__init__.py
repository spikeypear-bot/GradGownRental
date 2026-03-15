from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):  # ← THIS FUNCTION MISSING
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Init extensions
    db.init_app(app)
    
    # Register blueprints
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)
    
    return app
