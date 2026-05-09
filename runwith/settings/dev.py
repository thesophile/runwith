from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

#I entered this for media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


from dotenv import load_dotenv
import os

load_dotenv(BASE_DIR / 'runwith_dev.env') 