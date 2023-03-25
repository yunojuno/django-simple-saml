from urllib.parse import urlencode

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from social_django.utils import load_backend, load_strategy


def index(request: HttpRequest) -> HttpResponse:
    base_url = reverse("social:begin", kwargs={"backend": "saml"})
    params = urlencode({"next": "/", "idp": "test_idp"})
    context = {"test_idp": f"{base_url}?{params}"}
    return render(request, "index.html", context)


def saml_metadata_view(request: HttpRequest) -> HttpResponse:
    complete_url = reverse("social:complete", args=("saml",))
    saml_backend = load_backend(
        load_strategy(request), "saml", redirect_uri=complete_url
    )
    metadata, errors = saml_backend.generate_metadata_xml()
    if not errors:
        return HttpResponse(content=metadata, content_type="text/xml")
