from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from simple_saml.models import IdentityProvider


def index(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated and not request.user.is_staff:
        auth = request.user.social_auth.get()
    else:
        auth = None
    return render(
        request,
        "index.html",
        {"identity_providers": IdentityProvider.objects.active(), "auth": auth},
    )
