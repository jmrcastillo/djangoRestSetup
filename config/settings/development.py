# settings/development.py

from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1'
]

# Jwt setup
JWT_REFRESH_COOKIE_NAME = "refresh_token"
JWT_COOKIE_HTTPONLY = True
JWT_COOKIE_SECURE = not DEBUG
JWT_COOKIE_SAMESITE = "Lax"
JWT_COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Next.js dev server
    "http://localhost:8081", # React Native dev server
    "http://127.0.0.1:8081", # React Native dev server
    "http://192.168.100.199:8081", # React Native dev server
    "https://9pcmf38-anonymous-8081.exp.direct" # React Native Dev Server
]

# Mobile - Expo React Native
# for expo dynamically changes
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.exp\.direct$",
    r"^http://.*\.exp\.direct$",
]

CORS_ALLOW_CREDENTIALS = True
