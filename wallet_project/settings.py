from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# VULN-07: hardcoded secrets, debug on, any host allowed
SECRET_KEY = "django-insecure-9f$k2!wallet-dev-key-do-not-ship"
JWT_SECRET = "wallet123"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "rest_framework",
    "drf_spectacular",
    "wallet",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "wallet_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {},
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["wallet.auth.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "UNAUTHENTICATED_USER": None,
    # VULN-05b: no throttling configured anywhere
}

SPECTACULAR_SETTINGS = {
    "TITLE": "leaky-ledger",
    "DESCRIPTION": "Deliberately vulnerable wallet API. Localhost only.",
    "VERSION": "2.0.0",
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
