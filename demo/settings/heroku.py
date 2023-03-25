# Parse database configuration from $DATABASE_URL
import dj_database_url

from .base import *

DATABASES["default"] = dj_database_url.config()
