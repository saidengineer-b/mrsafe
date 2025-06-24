"""
Django settings for mrsafe.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")  # ✅ Proper call

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")




OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ Ensure OpenAI API Key is set
if not OPENAI_API_KEY:
    print("[ERROR] OpenAI API Key is missing or not loaded!")
else:
    print(f"[DEBUG] OpenAI API Key Loaded: {OPENAI_API_KEY[:5]}... (Masked for Security)")

# ✅ Custom User Model
AUTH_USER_MODEL = "mrsafe_app.CustomUser"

# ✅ Security settings
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "your-strong-secret-key")  # Use env variable
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"  # Environment-based debug mode

# ✅ Allowed Hosts
ALLOWED_HOSTS = [
    "192.168.1.73", "192.168.1.78", "192.168.3.39",
    "192.168.1.202", "166.87.229.1", "localhost", "127.0.0.1", "*"
]

# ✅ Installed Apps
INSTALLED_APPS = [
    # ✅ Ensure this is FIRST
    
    "mrsafe_app",  # ✅ Correct app name
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "widget_tweaks",
      # ✅ Correctly added 'channels'
     'ckeditor_uploader',  # ✅ Correct

      'django.contrib.sites',

]
ASGI_APPLICATION = "mrsafe_app.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",  # ✅ Local development
    }
}



# ✅ Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ✅ Root URL Configuration
ROOT_URLCONF = "mrsafe_project.urls"

# ✅ Templates Configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],  # ✅ Ensure this is correct
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

# ✅ WSGI Application
WSGI_APPLICATION = "mrsafe_project.wsgi.application"

# ✅ Database (MySQL)
# ✅ Database (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mrsafe',
        'USER': 'postgres',
        'PASSWORD': 'Razan@1978',  # Replace with the actual password you set
        'HOST': 'localhost',
        'PORT': '5432',          # ✅ Must be 5432, not 5433
    }
}



# ✅ Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ✅ Internationalization
LANGUAGES = [
    ("en", "English"),
    ("ar", "Arabic"),
]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ✅ Static Files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ✅ Media Files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"





# ✅ Email Settings (Use Env Variables in Production)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.secureserver.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
ADMIN_EMAIL = EMAIL_HOST_USER


DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "sales@mrsafe-ai.net")

# ✅ Login and Logout Redirects
LOGIN_REDIRECT_URL = "/mrsafe/"  # ✅ Redirect users to mrsafezes section
LOGOUT_REDIRECT_URL = "/"

# ✅ Locale Paths
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

# ✅ Language Support
USE_I18N = True
USE_L10N = True

# Google Pay Settings
GOOGLE_PAY_MERCHANT_ID = "your-merchant-id"
GOOGLE_PAY_GATEWAY = "example"
GOOGLE_PAY_API_VERSION = 2
GOOGLE_PAY_ENVIRONMENT = "TEST"  # Change to "PRODUCTION" when live



BRAINTREE_MERCHANT_ID = 'xd48m5jj2s9pfbyv'
BRAINTREE_PUBLIC_KEY = 'hb547fq5949v7hkk'
BRAINTREE_PRIVATE_KEY = '2681392394c97bb2f726fd0aa9df1ac4'
BRAINTREE_ENVIRONMENT = 'sandbox'  # or 'production' later




CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Full',
        'height': 300,
        'width': 'auto',
        'extraPlugins': 'uploadimage,image2',
        'extraPlugins': 'image2',
    }
}
SITE_URL = "http://127.0.0.1:8000"

SITE_ID = 1

