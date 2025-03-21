from backend.settings import *

DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
]

# Cors Config
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
]

# Pusher
PUSHER_APP_ID = os.environ.get('PUSHER_APP_ID_DEV')
PUSHER_KEY = os.environ.get('PUSHER_KEY_DEV')
PUSHER_SECRET = os.environ.get('PUSHER_SECRET_DEV')
PUSHER_CLUSTER = os.environ.get('PUSHER_CLUSTER')
