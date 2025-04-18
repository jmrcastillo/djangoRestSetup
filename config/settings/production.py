# settings/production.py

from .base import *
from decouple import config

DEBUG = False

ALLOWED_HOSTS = ['yourdomain.com']

# DATABASES = {
    # 'default': {
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': config('POSTGRES_DB'),
        # 'USER': config('POSTGRES_USER'),
        # 'PASSWORD': config('POSTGRES_PASSWORD'),
        # 'HOST': config('POSTGRES_HOST', 'localhost'),
        # 'PORT': config('POSTGRES_PORT', '5432'),
    # }
# }

# Add production-specific settings like security headers, etc.

