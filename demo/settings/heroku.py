# Parse database configuration from $DATABASE_URL
import dj_database_url

from .base import *

DATABASES["default"] = dj_database_url.config()

# generate with OpenSSL and store in environment variable
SOCIAL_AUTH_SAML_SP_PUBLIC_CERT = getenv("SAML_PUBLIC_CERT")

# generate with OpenSSL and store in environment variable
SOCIAL_AUTH_SAML_SP_PRIVATE_KEY = getenv("SAML_PRIVATE_KEY")
