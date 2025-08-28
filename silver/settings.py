# Copyright (c) 2025 Orbbin 
# Licensed under the Apache License, Version 2.0 (the "License");
# http://www.apache.org/licenses/LICENSE-2.0
import os
import datetime
import sys
import urllib.parse as urlparse

import environ

from silver import HOOK_EVENTS as _HOOK_EVENTS
from django.utils.log import DEFAULT_LOGGING as LOGGING

"""
These settings are used by the ``manage.py`` command.
"""

# --- env & defaults -----------------------------------------------------------
# Load from .env if present (project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env = environ.Env(
    DEBUG=(bool, True),
    SILVER_DB_URL=(str, "postgres://appuser:appsecret@localhost:5432/appdb"),
    REDIS_URL=(str, "redis://redis:6379/0"),
    TIME_ZONE=(str, "UTC"),
)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

DEBUG = True
SITE_ID = 1

USE_TZ = True
TIME_ZONE = env("TIME_ZONE")

# --- database -----------------------------------------------------------------
try:
    DATABASES = {
        "default": env.db(
            "SILVER_DB_URL",
            default="sqlite:///%s" % os.path.join(os.path.dirname(__file__), "db.sqlite"),
        )
    }
except ImportError:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite",
        }
    }

# PyMySQL shim only if using MySQL (kept from original)
if "mysql" in DATABASES["default"]["ENGINE"]:
    try:
        import pymysql
        pymysql.version_info = (1, 4, 6, "final", 0)
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass

# --- apps ---------------------------------------------------------------------
EXTERNAL_APPS = [
    # Django autocomplete
    "dal",
    "dal_select2",

    # Django core apps
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",

    # Required apps
    "django_fsm",
    "rest_framework",
    "django_filters",

    # Dev tools
    # "django_extensions",
]

INTERNAL_APPS = [
    "silver",
]

INSTALLED_APPS = EXTERNAL_APPS + INTERNAL_APPS

ROOT_URLCONF = "silver.urls"
PROJECT_ROOT = os.path.dirname(__file__) + "/silver/"

FIXTURE_DIRS = (
    PROJECT_ROOT,
    PROJECT_ROOT + "/silver/",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [
            PROJECT_ROOT + "/payment_processors/templates/",
            PROJECT_ROOT + "/templates/",
            PROJECT_ROOT + "/silver/templates/",
        ],
        "OPTIONS": {
            "context_processors": (
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
            )
        },
    }
]

MEDIA_ROOT = PROJECT_ROOT + "/app_media/"
MEDIA_URL = "/app_media/"

# STATIC_ROOT = PROJECT_ROOT + "/app_static/"
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'app_static'),
# ]
# STATIC_URL = "/app_static/"

STATIC_URL = '/app_static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'app_static'),
]


MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

SECRET_KEY = "secret"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_PAGINATION_CLASS": "silver.api.pagination.LinkHeaderPagination",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

HOOK_EVENTS = _HOOK_EVENTS

SILVER_DEFAULT_DUE_DAYS = 5
SILVER_DOCUMENT_PREFIX = "documents/"
SILVER_DOCUMENT_STORAGE = None
SILVER_PAYMENT_TOKEN_EXPIRATION = datetime.timedelta(minutes=5)
SILVER_AUTOMATICALLY_CREATE_TRANSACTIONS = True

# --- logging ------------------------------------------------------------------
LOGGING["loggers"]["xhtml2pdf"] = {"level": "DEBUG", "handlers": ["console"]}
LOGGING["loggers"]["pisa"] = {"level": "DEBUG", "handlers": ["console"]}
LOGGING["loggers"]["django"] = {"level": "DEBUG", "handlers": ["console"]}
LOGGING["loggers"]["django.security"] = {"level": "DEBUG", "handlers": ["console"]}
LOGGING["formatters"] = LOGGING.get("formatters", {})
LOGGING["formatters"]["verbose"] = {
    "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
    "datefmt": "%d/%b/%Y %H:%M:%S",
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

PAYMENT_PROCESSORS = {
    "manual": {
        "class": "silver.payment_processors.manual.ManualProcessor"
    },
}

PAYMENT_METHOD_SECRET = b"YOUR_FERNET_KEY_HERE"  # Fernet.generate_key()

# --- Redis / Celery / Lock manager -------------------------------------------
REDIS_URL = env("REDIS_URL")  # e.g. redis://localhost:6379/0

CELERY_BROKER_URL = REDIS_URL
CELERY_BEAT_SCHEDULE = {
    "generate-pdfs": {
        "task": "silver.tasks.generate_pdfs",
        "schedule": datetime.timedelta(seconds=5),
    },
}

# Parse REDIS_URL into host/port/db for the lock manager
_parsed = urlparse.urlparse(REDIS_URL)
_lock_db = int((_parsed.path or "/0").lstrip("/")) if (_parsed.path and _parsed.path != "/") else 0
LOCK_MANAGER_CONNECTION = {
    "host": _parsed.hostname or "localhost",
    "port": int(_parsed.port or 6379),
    "db": _lock_db,
}

# Optional: cache via django-redis if you have it installed
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "TIMEOUT": 300,
    }
}

PDF_GENERATION_TIME_LIMIT = 60
TRANSACTION_SAVE_TIME_LIMIT = 5

# --- local overrides ----------------------------------------------------------
try:
    from settings_local import *  # noqa
except ImportError:
    pass

# --- test knobs ---------------------------------------------------------------
if sys.argv[0].endswith("pytest"):
    from silver.fixtures.test_fixtures import PAYMENT_PROCESSORS  # noqa
    PAYMENT_DUE_DAYS = 5
    REST_FRAMEWORK["PAGE_SIZE"] = API_PAGE_SIZE = 5
    SILVER_SHOW_PDF_STORAGE_URL = True

# Celery Once configuration for task deduplication
CELERY_ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': REDIS_URL,  # Uses your existing REDIS_URL
        'default_timeout': 60 * 60,  # 1 hour
    }
}

# Ensure media directory exists
os.makedirs(MEDIA_ROOT, exist_ok=True)

# Windows-specific Celery settings (only when not using Docker)
if not os.environ.get('CELERY_WORKER_IN_DOCKER') and sys.platform == 'win32':
    CELERY_WORKER_POOL = 'threads'
    CELERY_WORKER_CONCURRENCY = 4
    CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Add at the very end of the file, before the test knobs section:

# --- Docker environment detection ---
CELERY_WORKER_IN_DOCKER = os.environ.get('CELERY_WORKER_IN_DOCKER', False)

# DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("SILVER_DB_URL")

# if DATABASE_URL:
#     parsed = urlparse(DATABASE_URL)
#     DATABASES = {
#         "default": {
#             "ENGINE": "django.db.backends.postgresql",
#             "NAME": parsed.path.lstrip("/"),
#             "USER": parsed.username,
#             "PASSWORD": parsed.password,
#             "HOST": parsed.hostname,
#             "PORT": parsed.port or 5432,
#         }
#     }
# else:
#     DATABASES = {
#         "default": {
#             "ENGINE": "django.db.backends.postgresql",
#             "NAME": os.environ.get("POSTGRES_DB", "appdb"),
#             "USER": os.environ.get("POSTGRES_USER", "appuser"),
#             "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "appsecret"),
#             "HOST": os.environ.get("POSTGRES_HOST", "postgres"),   # <-- IMPORTANT
#             "PORT": os.environ.get("POSTGRES_PORT", "5432"),
#         }
#     }
