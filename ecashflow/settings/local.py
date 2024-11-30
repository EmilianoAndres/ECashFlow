from .base import *

from os import path 
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['ecashflow.online', 'localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ["https://ecashflow.online"]

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
# Absolute filesystem path to the directory that will hold static files.
#STATIC_ROOT = path.join(BASE_DIR, 'static')

STATICFILES_DIRS = path.join(BASE_DIR, 'static'),


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'