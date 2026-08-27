from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG')

# ALLOWED_HOSTS = ['runwith.cloud', 'www.runwith.cloud', 'manim.runwith.cloud']
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

#I entered this for media
MEDIA_URL = 'https://runwith.cloud/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

from dotenv import load_dotenv
import os

load_dotenv(BASE_DIR / 'runwith_prod.env') 

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("The DJANGO_SECRET_KEY environment variable is not set.")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': '',
        'PORT': '',
    }
}

# CSRF and Cookie Security Settings
# CSRF_TRUSTED_ORIGINS = ["https://runwith.cloud", "https://www.runwith.cloud", "https://manim.runwith.cloud"]
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")

# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = os.environ.get("cookie_secure", "True").lower() == "true"
SESSION_COOKIE_SECURE = os.environ.get("cookie_secure", "True").lower() == "true"


#so that login in any app ensures login in all apps
# SESSION_COOKIE_DOMAIN = ".runwith.cloud"
# CSRF_COOKIE_DOMAIN = ".runwith.cloud"

SESSION_COOKIE_DOMAIN = os.environ.get("SESSION_COOKIE_DOMAIN") or None
CSRF_COOKIE_DOMAIN = os.environ.get("CSRF_COOKIE_DOMAIN") or None