from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

#I entered this for media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# dev.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

from dotenv import load_dotenv
from django.core.management.utils import get_random_secret_key
import os

load_dotenv(BASE_DIR / 'runwith_dev.env') 

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

if not SECRET_KEY:
    try:
        SECRET_KEY = get_random_secret_key()
    except:
        raise ValueError("The DJANGO_SECRET_KEY environment variable is not set. Do you have runwith_dev.env? See the docs")
    
