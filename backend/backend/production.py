from backend.settings import *

DEBUG = False

ALLOWED_HOSTS = [
    "https://skillhub-api-9mkx.onrender.com",
]

# Cors Config
CORS_ALLOWED_ORIGINS = [
    "https://skillhub-qgfd.onrender.com",
]

# Pusher
PUSHER_CLUSTER = os.environ.get('PUSHER_CLUSTER')
PUSHER_APP_ID = os.environ.get('PUSHER_APP_ID_PROD')
PUSHER_KEY = os.environ.get('PUSHER_KEY_PROD')
PUSHER_SECRET = os.environ.get('PUSHER_SECRET_PROD')
