from .base import *  # noqa: F401,F403
from decouple import config, Csv

DEBUG = True

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="giftly"),
        "USER": config("POSTGRES_USER", default="giftly"),
        "PASSWORD": config("POSTGRES_PASSWORD", default="giftly"),
        "HOST": config("POSTGRES_HOST", default="db"),  # docker-compose service nomi
        "PORT": config("POSTGRES_PORT", default="5432"),
    }
}

INSTALLED_APPS += ["rest_framework.authtoken"]  # noqa: F405
