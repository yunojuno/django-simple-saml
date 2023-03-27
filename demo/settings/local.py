from .base import *  # noqa: F403

ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".ngrok.io"]

DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3", "NAME": "demo.db"}

# required for running against https://localhost:8000 as the SP
INSTALLED_APPS += ["sslserver"]  # noqa: F405

if not SOCIAL_AUTH_SAML_SP_PUBLIC_CERT:
    with open("saml.crt") as f:
        SOCIAL_AUTH_SAML_SP_PUBLIC_CERT = f.read()

if not SOCIAL_AUTH_SAML_SP_PRIVATE_KEY:
    with open("saml.key") as f:
        SOCIAL_AUTH_SAML_SP_PRIVATE_KEY = f.read()
