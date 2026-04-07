import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.environ.get('ERROR_DB_USER', 'error_user')}:"
        f"{os.environ.get('ERROR_DB_PASSWORD')}@"
        f"{os.environ.get('ERROR_DB_HOST', 'localhost')}:"
        f"{os.environ.get('ERROR_DB_PORT', '5432')}/"
        f"{os.environ.get('ERROR_DB_NAME', 'error')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NOTIFICATION_SERVICE_URL = os.environ.get('NOTIFICATION_SERVICE_URL', 'http://localhost:5001')
