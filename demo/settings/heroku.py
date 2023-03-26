# Parse database configuration from $DATABASE_URL
import dj_database_url

from .base import *

ALLOWED_HOSTS = [".herokuapp.com"]

DATABASES["default"] = dj_database_url.config()
