from .base import *  # noqa: F403

DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3", "NAME": "demo.db"}

with open("saml.crt") as f:
    SOCIAL_AUTH_SAML_SP_PUBLIC_CERT = f.read()

with open("saml.key") as f:
    SOCIAL_AUTH_SAML_SP_PRIVATE_KEY = f.read()
