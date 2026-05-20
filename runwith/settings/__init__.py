# project/settings/__init__.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / 'runwith_dev.env') 

env = os.environ.get("DJANGO_ENV", "prod")

if env == "dev":
    from .dev import *
    print('running in development')
else:
    from .prod import *
    print('running in production')
