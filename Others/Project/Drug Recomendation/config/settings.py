"""
Django settings for AI-Based Drug Recommendation System.
Configured for development with SQLite and production readiness for PostgreSQL.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Security configuration
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-academic-clinical-decision-support-key-change-in-prod-77a83b9c'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost,testserver').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Core system modules
    'accounts.apps.AccountsConfig',
    'medical.apps.MedicalConfig',
    'symptoms.apps.SymptomsConfig',
    'ml_engine.apps.MlEngineConfig',
    'recommendations.apps.RecommendationsConfig',
    'dashboard.apps.DashboardConfig',
    'reports.apps.ReportsConfig',
    'audit.apps.AuditConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dashboard.context_processors.notification_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Default: SQLite3 for agile local development; easily switched to PostgreSQL via DATABASE_URL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static and Media Files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication Redirections
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:role_redirect'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Session & Security Settings
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400  # 24 hours
CSRF_COOKIE_HTTPONLY = False  # Allows AJAX fetch to read CSRF if required
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
