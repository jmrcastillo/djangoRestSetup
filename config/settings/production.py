# settings/production.py

from .base import *
from decouple import config
import os
import environ

DEBUG = False

SECRET_KEY = os.environ.get("SECRET_KEY", "unsafe-dev-key")
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = ['yourdomain.com']

# SSL & CSRF
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = [
    "https://upland-api-production-001e.up.railway.app",
    "https://upland-frontend-nu.vercel.app"
]

# Allow your Vercel frontend
CORS_ALLOWED_ORIGINS = [
    "https://upland-frontend-git-main-jmrcas-projects.vercel.app",
    "https://upland-frontend-nu.vercel.app",
]

CORS_ALLOW_CREDENTIALS = True


BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Postgresql & Env Variable
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('PGDATABASE'),
        'USER': env('PGUSER'),
        'PASSWORD': env('PGPASSWORD'),
        'HOST': env('PGHOST'),
        'PORT': env('PGPORT'),
    }
}

# Add production-specific settings like security headers, etc.

