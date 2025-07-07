from pathlib import Path
import os
import dj_database_url  # ✅ Add this for Render DB compatibility

BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 SECURITY
SECRET_KEY = 'django-insecure-k()jvyk^=!1%hguv89d8n%y4(+vv47%h0#8l!i-8jfp21fexxe'
DEBUG = True  # Set to False in production
ALLOWED_HOSTS = ['*']  # You can restrict this later

# ✅ Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'star_cinema_app',
    'cloudinary',
    'cloudinary_storage',
]

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


# ✅ Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ WhiteNoise right after security
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'StarCinemaProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'StarCinemaProject.wsgi.application'

# ✅ DATABASE
if os.environ.get('RENDER'):
    DATABASES = {
        'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
    }
else:
    # For local development (keep your MySQL if needed)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'StarCinema',
            'USER': 'root',
            'PASSWORD': '',
            'HOST': '127.0.0.1',
            'PORT': '3307',
        }
    }


# If using DATABASE_URL from environment (optional)
# DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=False)

# 🔒 Password Validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 🌍 Localization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ✅ Static Files (CSS, JS)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ✅ Media Files (for uploaded images)
# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default PK type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dyudlsi2v',
    'API_KEY': '682369582911734',
    'API_SECRET': '71Ga4Sfn2NV4XiFtQhaKnS4AbdM',
}