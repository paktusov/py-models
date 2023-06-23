import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

PRODUCTION = os.getenv('PRODUCTION')

S3_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY_ID')
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SPACE_NAME = os.getenv('S3_SPACE_NAME')
S3_REGION_NAME = os.getenv('S3_REGION_NAME')
S3_ENDPOINT = "https://{}.{}.digitaloceanspaces.com".format(S3_SPACE_NAME, S3_REGION_NAME)
S3_CDN_ENDPOINT = "https://{}.{}.cdn.digitaloceanspaces.com".format(S3_SPACE_NAME, S3_REGION_NAME)

VERYFI_CLIENT_ID = os.getenv('VERYFI_CLIENT_ID')
VERYFI_CLIENT_SECRET = os.getenv('VERYFI_CLIENT_SECRET')
VERYFI_USERNAME = os.getenv('VERYFI_USERNAME')
VERYFI_API_KEY = os.getenv('VERYFI_API_KEY')

TWILIO_ACCOUNT = os.getenv('TWILIO_ACCOUNT')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')

ORDER_LIMIT_EXPIRE_MIN = 60
APPO_LIMIT_EXPIRE_DAY = 1

BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_CHAT_DEV = "-763564222"
BOT_CHAT_CARSAN_MAIN = "-1001681437126"

SQLALCHEMY_POOL_RECYCLE = 299
SQLALCHEMY_POOL_TIMEOUT = 300
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_TRACK_MODIFICATIONS = False

# APP TYPE
# APP_TYPE = os.getenv("APP_TYPE")
# SESSION_KEY_PREFIX = APP_TYPE
SECRET_KEY = os.getenv("SECRET_KEY_ADMIN")

PLATFORM = 'STAG' if os.getenv('STAGING') else 'PROD'

if os.getenv('PRODUCTION'):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_PROD')
    BOT_CHAT_ID_LIST = [BOT_CHAT_DEV, BOT_CHAT_CARSAN_MAIN]
    if os.getenv('STAGING'):
        HOST_API = "https://api-stage-x9ujm.ondigitalocean.app"
        HOST_URL = "https://cars.gocrsn.com"
        STRIPE_API_KEY = os.getenv('STRIPE_API_KEY_DEV')
        STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_KEY_STAGING')
        HOST_URL_ADM = "https://officestage.gocrsn.com"
    else:
        HOST_API = "https://api.carsan.com"
        HOST_URL = "https://cars.carsan.com"
        STRIPE_API_KEY = os.getenv('STRIPE_API_KEY_PROD')
        STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_KEY_PROD')
        HOST_URL_ADM = "https://office.gocrsn.com"
    CELERY_BROKER_URL = os.getenv('RABBIT_PROD')
    # CELERY_RESULT_BACKEND = f"redis://{os.getenv('REDIS_PROD')}"
    # use filesystem as result backend (fuck you redis)
    CELERY_RESULT_BACKEND = f"file://{tempfile.gettempdir()}"
    # CELERY_REDIS_HOST = '10.124.0.4'
    PARSER_HOST = 'http://10.124.0.4:6000'
    WORKER = os.getenv('WORKER_PROD')
else:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_DEV')
    BOT_CHAT_ID_LIST = ["-837914949"]
    HOST_API = "https://api.carsan.com"
    STRIPE_API_KEY = os.getenv('STRIPE_API_KEY_DEV')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_KEY_DEV')
    HOST_URL = "http://cars.carsana:9090"
    HOST_URL_ADM = "http://gocrsn:5000"
    WORKER = os.getenv('WORKER_DEV')
    # BROKER_URL = os.getenv('RABBIT_DEV')
    # CELERY_RESULT_BACKEND = "redis://@{}".format(os.getenv('REDIS_DEV'))

    # celery setup
    CELERY_BROKER_URL = os.getenv('RABBIT_DEV')
    # redis://redis:6379/0
    # CELERY_RESULT_BACKEND = "redis://{}".format(os.getenv('REDIS_DEV'))
    # CELERY_REDIS_HOST = 'redis'
    # use filesystem as result backend
    CELERY_RESULT_BACKEND = f"file://{tempfile.gettempdir()}"
    PARSER_HOST = 'http://parser:6060'
