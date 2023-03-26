from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from simple_saml.models import IdentityProvider


def index(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "index.html",
        {"identity_providers": IdentityProvider.objects.active()},
    )
