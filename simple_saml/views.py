from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from social_django.utils import load_backend, load_strategy


@user_passes_test(lambda u: u.is_superuser)
def saml_metadata_view(request: HttpRequest) -> HttpResponse:
    """View to generate the SAML metadata XML (superuser only)."""
    uri = (reverse("social:complete", args=("saml",)),)
    saml_backend = load_backend(load_strategy(request), "saml", redirect_uri=uri)
    metadata, errors = saml_backend.generate_metadata_xml()
    if not errors:
        return HttpResponse(content=metadata, content_type="text/xml")
    raise Exception("Error loading SAML backend.")
