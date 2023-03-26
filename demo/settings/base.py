from os import getenv, path

DEBUG = bool(getenv("DJANGO_DEBUG", False))
TEMPLATE_DEBUG = DEBUG
USE_TZ = True

DATABASES = {}

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "social_django",
    "demo",
)

MIDDLEWARE = [
    # default django middleware
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
STATIC_ROOT = path.join(PROJECT_DIR, "staticfiles")

SECRET_KEY = getenv("DJANGO_SECRET_KEY")

# Ensures that the request is secure when running behind a proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

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
    # "social_core.backends.saml.SAMLAuth",
    "demo.saml.SAMLAuth",
    "django.contrib.auth.backends.ModelBackend",
)

LOGIN_REDIRECT_URL = "/"

# ====== SAML SETTINGS ======
#
# The SAML Entity ID for your app. This should be a URL that includes a
# domain name you own. It doesn’t matter what the URL points to.
SOCIAL_AUTH_SAML_SP_ENTITY_ID = getenv("SAML_SP_ENTITY_ID", "https://localhost")

# The X.509 certificate string for the key pair that your app will use.
# You can generate a new self-signed key pair with:
# openssl req -new -x509 -days 3652 -nodes -out saml.crt -keyout saml.key
SOCIAL_AUTH_SAML_SP_PUBLIC_CERT = getenv(
    "SAML_SP_PUBLIC_CERT", "GENERATE THIS WITH OPENSSL"
)


# The private key to be used by your app. If you used the example
# openssl command given above, set this to the contents of saml.key
# (again, you can omit the first and last lines).
SOCIAL_AUTH_SAML_SP_PRIVATE_KEY = getenv(
    "SAML_SP_PRIVATE_KEY", "GENERATE THIS WITH OPENSSL"
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


# THIS IS NOW READ FROM THE DATABASE - SEE saml.py
# The most important setting. List the Entity ID, SSO URL, and x.509
# public key certificate for each provider that your app wants to
# support. The SSO URL must support the HTTP-Redirect binding. You can
# get these values from the provider’s XML metadata.
# SOCIAL_AUTH_SAML_ENABLED_IDPS = {}


# === SOCIAL_AUTH_APP_DJANGO SETTINGS ===

# When using PostgreSQL, it’s recommended to use the built-in JSONB
# field to store the extracted extra_data.
SOCIAL_AUTH_JSONFIELD_ENABLED = True

SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. In some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    "social_core.pipeline.social_auth.social_details",
    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    "social_core.pipeline.social_auth.social_uid",
    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    "social_core.pipeline.social_auth.auth_allowed",
    # Checks if the current social-account is already associated in the site.
    "social_core.pipeline.social_auth.social_user",
    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    "social_core.pipeline.user.get_username",
    # Send a validation email to the user to verify its email address.
    # Disabled by default.
    # 'social_core.pipeline.mail.mail_validation',
    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    "social_core.pipeline.social_auth.associate_by_email",
    # Create a user account if we haven't found one yet.
    "social_core.pipeline.user.create_user",
    # Create the record that associates the social account with the user.
    "social_core.pipeline.social_auth.associate_user",
    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    "social_core.pipeline.social_auth.load_extra_data",
    # Update the user record with any changed info from the auth service.
    "social_core.pipeline.user.user_details",
)
