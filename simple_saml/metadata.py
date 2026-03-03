import logging

from django.http import HttpRequest
from django.urls import reverse
from social_django.utils import load_backend, load_strategy

from .exceptions import MetadataException

logger = logging.getLogger(__name__)


def get_saml_metadata(request: HttpRequest, redirect_uri: str = "") -> str:
    """Return the SAML Service Provider XML."""
    redirect_uri = redirect_uri or reverse("social:complete", args=("saml",))
    strategy = load_strategy(request)
    backend = load_backend(strategy, "saml", redirect_uri=redirect_uri)
    metadata, errors = backend.generate_metadata_xml()
    if not errors:
        return metadata
    # Log specific backend errors while keeping the raised exception message generic.
    logger.error("Error loading SAML backend: %s", errors)
    raise MetadataException(backend_errors=tuple(map(str, errors)))
