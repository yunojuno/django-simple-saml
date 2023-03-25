from os import getenv, path

DEBUG = True
TEMPLATE_DEBUG = True
USE_TZ = True
USE_L10N = True

DATABASES = {}

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "social_django",
)

MIDDLEWARE = [
    # default django middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

# we must come up one directory as we are in demo/settings
PROJECT_DIR = path.abspath(path.join(path.dirname(__file__), ".."))

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [path.join(PROJECT_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.messages.context_processors.messages",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
            ]
        },
    }
]

STATIC_URL = "/static/"

SECRET_KEY = getenv("DJANGO_SECRET_KEY")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "%(levelname)s %(message)s"}},
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        }
    },
    "loggers": {
        "": {"handlers": ["console"], "propagate": True, "level": "DEBUG"},
        # 'django': {
        #     'handlers': ['console'],
        #     'propagate': True,
        #     'level': 'WARNING',
        # },
    },
}

ROOT_URLCONF = "demo.urls"


AUTHENTICATION_BACKENDS = (
    "social_core.backends.saml.SAMLAuth",
    "django.contrib.auth.backends.ModelBackend",
)

if not DEBUG:
    raise Exception("This settings file can only be used with DEBUG=True")

# ====== SAML SETTINGS ======
#
# The SAML Entity ID for your app. This should be a URL that includes a
# domain name you own. It doesn’t matter what the URL points to.
SOCIAL_AUTH_SAML_SP_ENTITY_ID = "https://localhost:8000/saml2/acs/"

# The X.509 certificate string for the key pair that your app will use.
# You can generate a new self-signed key pair with:
# openssl req -new -x509 -days 3652 -nodes -out saml.crt -keyout saml.key
SOCIAL_AUTH_SAML_SP_PUBLIC_CERT = getenv(
    "SAML_PUBLIC_CERT", "GENERATE THIS WITH OPENSSL"
)


# The private key to be used by your app. If you used the example
# openssl command given above, set this to the contents of saml.key
# (again, you can omit the first and last lines).
SOCIAL_AUTH_SAML_SP_PRIVATE_KEY = getenv(
    "SAML_PRIVATE_KEY", "GENERATE THIS WITH OPENSSL"
)


# A dictionary that contains information about your app. You must
# specify values for English at a minimum. Each language’s entry should
# specify a name (not shown to the user), a displayname (shown to the
# user), and a URL.
SOCIAL_AUTH_SAML_ORG_INFO = {
    "en-US": {
        "name": "yunojuno",
        "displayname": "YunoJuno",
        "url": "http://yunojuno.com",
    }
}

# A dictionary with two values, givenName and emailAddress, describing
# the name and email of a technical contact responsible for your app.
SOCIAL_AUTH_SAML_TECHNICAL_CONTACT = {
    "givenName": "YunoJuno Tech Support",
    "emailAddress": "code@yunojuno.com",
}

# A dictionary with two values, givenName and emailAddress, describing
# the name and email of a support contact for your app.
SOCIAL_AUTH_SAML_SUPPORT_CONTACT = {
    "givenName": "YunoJuno Support",
    "emailAddress": "hello@yunojuno.com",
}

# The most important setting. List the Entity ID, SSO URL, and x.509
# public key certificate for each provider that your app wants to
# support. The SSO URL must support the HTTP-Redirect binding. You can
# get these values from the provider’s XML metadata.
SOCIAL_AUTH_SAML_ENABLED_IDPS = {
    "test_idp": {
        "entity_id": getenv("SAML_ENTITY_ID"),
        "url": getenv("SAML_SSO_URL"),
        "x509cert": getenv("SAML_X509_CERT"),
    }
}

# === SOCIAL_AUTH_APP_DJANGO SETTINGS ===
# When using PostgreSQL, it’s recommended to use the built-in JSONB
# field to store the extracted extra_data.
SOCIAL_AUTH_JSONFIELD_ENABLED = True
