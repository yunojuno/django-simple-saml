from __future__ import annotations

from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _lazy


class IdentityProviderManager(models.Manager):
    """Custom manager for the IdentityProvider model."""

    def active(self) -> models.QuerySet[IdentityProvider]:
        """Return only the active IdentityProviders."""
        return self.get_queryset().filter(is_enabled=True)


class IdentityProvider(models.Model):
    """Class to store the Identity Provider metadata."""

    label = models.CharField(
        max_length=255,
        unique=True,
        help_text=_lazy(
            "A unique label / key used to identify the IdP to use. "
            "(Recommended value is the name or URL of the IdP.)"
        ),
    )
    entity_id = models.CharField(
        max_length=255,
        help_text=_lazy("The entity ID provided by the IdP."),
        verbose_name="Entity ID",
    )
    sso_url = models.CharField(
        max_length=255,
        help_text=_lazy("The SSO URL provided by the IdP."),
        verbose_name="SSO URL",
    )
    x509_cert = models.TextField(
        help_text=_lazy("The X.509 certificate provided by the IdP."),
        verbose_name="X509 Certificate",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_lazy(
            "Configuration keys to avoid having to use uniform resource name's as "
            "attributes to map user details required to complete account creation."
        ),
    )
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = IdentityProviderManager()

    def __str__(self) -> str:
        return self.label

    def save(self, *args: Any, **kwargs: Any) -> IdentityProvider:
        if "update_fields" in kwargs:
            kwargs["update_fields"] += ["updated_at"]
        return super().save(*args, **kwargs)

    @property
    def config(self) -> dict[str, str]:
        # returns the config for the get_idp method
        return {
            "entity_id": self.entity_id,
            "url": self.sso_url,
            "x509cert": self.x509_cert,
        } | self.metadata
