from decouple import Csv, config

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="giftly"),
        "USER": config("POSTGRES_USER", default="giftly"),
        "PASSWORD": config("POSTGRES_PASSWORD", default="giftly"),
        "HOST": config("POSTGRES_HOST", default="db"),
        "PORT": config("POSTGRES_PORT", default="5432"),
        "CONN_MAX_AGE": 60,
    }
}

# Dev muhitda CORS — frontend dev server
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000",
    cast=Csv(),
)

# Dev da email konsolga chiqadi
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
