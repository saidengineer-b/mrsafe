"""
Django settings for Mr. Safe
"""

import os
from pathlib import Path
from dotenv import load_dotenv

import dj_database_url
load_dotenv()
# ✅ Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ Load .env for local dev
load_dotenv(dotenv_path=BASE_DIR / ".env")

# ✅ Environment Variables
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "your-strong-default-secret-key")
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"
# REMOVE THIS if you're not setting DJANGO_ALLOWED_HOSTS in Railway/ENV:
# ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

# ✅ This is correct for production:
ALLOWED_HOSTS = ['www.mrsafe.me', 'mrsafe.me', '127.0.0.1', 'localhost']

# ✅ CSRF trusted domains:
CSRF_TRUSTED_ORIGINS = [
    'https://www.mrsafe.me',
    'https://mrsafe.me'
]



# ✅ OpenAI Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("[ERROR] OpenAI API Key is missing!")
else:
    print(f"[DEBUG] OpenAI Key Loaded: {OPENAI_API_KEY[:5]}...")

# ✅ Installed Apps
INSTALLED_APPS = [
    "mrsafe_app",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "widget_tweaks",
    "ckeditor_uploader",
    "django.contrib.sites",
]

# ✅ Middleware (WhiteNoise Added)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ✅ Enables static files in production
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ✅ Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ROOT_URLCONF = "mrsafe_project.urls"
WSGI_APPLICATION = "mrsafe_project.wsgi.application"
ASGI_APPLICATION = "mrsafe_project.asgi.application"

# ✅ Database
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "mrsafe",
            "USER": "postgres",
            "PASSWORD": "Razan@1978",
            "HOST": "localhost",
            "PORT": "5432",
        }
    }

# ✅ Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# ✅ Authentication
AUTH_USER_MODEL = "mrsafe_app.CustomUser"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_REDIRECT_URL = "/mrsafe/"
LOGOUT_REDIRECT_URL = "/"

# ✅ Internationalization
LANGUAGE_CODE = "en"
LANGUAGES = [("en", "English"), ("ar", "Arabic")]
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = [BASE_DIR / "locale"]

# ✅ Static Files (WhiteNoise Setup)
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ✅ WhiteNoise Static Optimization
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ✅ Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.secureserver.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "sales@mrsafe-ai.net")

# ✅ CKEditor
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Full',
        'height': 300,
        'width': 'auto',
        'extraPlugins': 'uploadimage,image2',
    }
}

# ✅ Payment Gateway Settings
GOOGLE_PAY_MERCHANT_ID = "your-merchant-id"
GOOGLE_PAY_GATEWAY = "example"
GOOGLE_PAY_API_VERSION = 2
GOOGLE_PAY_ENVIRONMENT = "TEST"

BRAINTREE_MERCHANT_ID = os.getenv("BRAINTREE_MERCHANT_ID", "xd48m5jj2s9pfbyv")
BRAINTREE_PUBLIC_KEY = os.getenv("BRAINTREE_PUBLIC_KEY", "hb547fq5949v7hkk")
BRAINTREE_PRIVATE_KEY = os.getenv("BRAINTREE_PRIVATE_KEY", "2681392394c97bb2f726fd0aa9df1ac4")
BRAINTREE_ENVIRONMENT = os.getenv("BRAINTREE_ENVIRONMENT", "sandbox")

# ✅ Site ID & URL
SITE_ID = 1
SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:8000")
