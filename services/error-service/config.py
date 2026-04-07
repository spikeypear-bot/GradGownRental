import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    NOTIFICATION_SERVICE_URL = os.environ.get('NOTIFICATION_SERVICE_URL', 'http://localhost:5005')