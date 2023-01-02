from decouple import config
import cloudinary
import cloudinary.uploader
from pathlib import Path
from twilio.rest import Client
from fastapi_mail import ConnectionConfig


ROOT_PATH = Path(__file__).parent.parent

SECRET_KEY = config('SECRET_KEY')

SITE_NAME = config('SITE_NAME')

ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif"]

cloudinary.config(
    cloud_name=config('CLOUDINARY_CLOUD_NAME'),
    api_key=config('CLOUDINARY_API_KEY'),
    api_secret=config('CLOUDINARY_API_SECRET'),
)

DATABASES = {
    "DB_NAME": config("POSTGRES_DB"),
    "USER": config("POSTGRES_USER"),
    "PASSWORD": config("POSTGRES_PASSWORD"),
    "HOST": config("PG_HOST"),
    "PORT": config("PG_PORT"),
}

# SMTP SETTINGS
email_conf = ConnectionConfig(
    MAIL_USERNAME=config('MAIL_USERNAME'),
    MAIL_PASSWORD=config('MAIL_PASSWORD'),
    MAIL_FROM=config('DEFAULT_FROM_EMAIL'),
    MAIL_PORT=config('MAIL_PORT'),
    MAIL_SERVER=config('MAIL_SERVER'),
    MAIL_FROM_NAME=config('SITE_NAME'),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER='./apps/accounts/templates/accounts'
)

# SMS SETINGS
account_sid = config('TWILIO_ACCOUNT_SID')
auth_token = config('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

DEFAULT_FROM_PHONE = config('DEFAULT_FROM_PHONE')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')