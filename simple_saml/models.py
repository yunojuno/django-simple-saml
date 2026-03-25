from __future__ import annotations

from typing import Any, Literal, TypedDict, cast

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from .exceptions import IdentityProviderConfigurationError

RequestedAuthnContextComparisonValue = Literal["exact", "minimum", "maximum", "better"]
RequestedAuthnContextValue = bool | list[str]


class SamlSecurityConfig(TypedDict, total=False):
    requestedAuthnContext: RequestedAuthnContextValue
    requestedAuthnContextComparison: RequestedAuthnContextComparisonValue


REQUESTED_AUTHN_CONTEXT_COMPARISON_MAP: dict[
    str, RequestedAuthnContextComparisonValue
] = {
    "EXACT": "exact",
    "MINIMUM": "minimum",
    "MAXIMUM": "maximum",
    "BETTER": "better",
}


class IdentityProviderManager(models.Manager):
    """Custom manager for the IdentityProvider model."""

    def active(self) -> models.QuerySet[IdentityProvider]:
        """Return only the active IdentityProviders."""
        return self.get_queryset().filter(is_enabled=True)


class IdentityProvider(models.Model):
    """Class to store the Identity Provider metadata."""

    class RequestedAuthnContextMode(models.TextChoices):
        DISABLED = "DISABLED", _lazy("Disabled")
        PASSWORD = "PASSWORD", _lazy("PasswordProtectedTransport")
        CUSTOM = "CUSTOM", _lazy("Custom")

    class RequestedAuthnContextComparison(models.TextChoices):
        EXACT = "EXACT", _lazy("Exact")
        MINIMUM = "MINIMUM", _lazy("Minimum")
        MAXIMUM = "MAXIMUM", _lazy("Maximum")
        BETTER = "BETTER", _lazy("Better")

    label = models.CharField(
        max_length=255,
        unique=True,
        help_text=_lazy(
            "A unique label / key used to identify the IdP to use. "
            "(Recommended value is the name or URL of the IdP.)"
        ),
    )
    provider = models.CharField(
        max_length=255,
        help_text=_lazy("The name of the provider (e.g. Google Workspace, Okta)."),
        blank=True,
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
    # these user attributes are used to map user details required to
    # complete account creation, the model values determine the
    # attribute names used to map the user details.
    user_permanent_id_attr = models.CharField(
        max_length=255,
        help_text=_lazy(
            "The attribute provided by the IdP for the user's unique "
            "ID property (required)."
        ),
    )
    first_name_attr = models.CharField(
        blank=True,
        max_length=255,
        help_text=_lazy(
            "The name of the attribute provided by the IdP for the "
            "'user.first_name' property."
        ),
    )
    last_name_attr = models.CharField(
        blank=True,
        max_length=255,
        help_text=_lazy(
            "The name of the attribute provided by the IdP for "
            "'user.last_name' property"
        ),
    )
    email_attr = models.CharField(
        blank=True,
        max_length=255,
        help_text=_lazy(
            "The name of the attribute provided by the IdP for the "
            "'user.email' property."
        ),
    )
    username_attr = models.CharField(
        blank=True,
        max_length=255,
        help_text=_lazy(
            "The username attribute provided by the IdP for the "
            "'user.username' property."
        ),
    )
    requested_authn_context_mode = models.CharField(
        max_length=16,
        choices=RequestedAuthnContextMode.choices,
        default=RequestedAuthnContextMode.DISABLED,
        help_text=_lazy("How to populate the SAML RequestedAuthnContext for this IdP."),
    )
    requested_authn_context_values = models.JSONField(
        blank=True,
        default=list,
        help_text=_lazy(
            "Custom AuthnContextClassRef values for CUSTOM mode. "
            "Ignored for DISABLED and PASSWORD."
        ),
    )
    requested_authn_context_comparison = models.CharField(
        max_length=8,
        choices=RequestedAuthnContextComparison.choices,
        default=RequestedAuthnContextComparison.EXACT,
        help_text=_lazy(
            "RequestedAuthnContext comparison value passed to python3-saml."
        ),
    )
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = IdentityProviderManager()

    def __str__(self) -> str:
        if self.provider:
            return f"{self.label} ({self.provider})"
        return self.label

    def save(self, *args: Any, **kwargs: Any) -> IdentityProvider:
        if "update_fields" in kwargs:
            kwargs["update_fields"] += ["updated_at"]
        return super().save(*args, **kwargs)

    def clean(self) -> None:
        super().clean()
        if self.requested_authn_context_mode != self.RequestedAuthnContextMode.CUSTOM:
            return
        requested_authn_context_values, error_message = (
            self._normalize_requested_authn_context_values()
        )
        if error_message is not None:
            raise ValidationError(
                {"requested_authn_context_values": error_message},
            )
        self.requested_authn_context_values = requested_authn_context_values

    @property
    def user_attribute_map(self) -> dict[str, str]:
        # only return non-empty values, as social_auth does not handle
        # empty values well.
        if not self.user_permanent_id_attr:
            raise IdentityProviderConfigurationError(
                field_name="user_permanent_id_attr",
                idp_name=self.label or None,
            )
        return {
            k: v
            for k, v in {
                "attr_user_permanent_id": self.user_permanent_id_attr,
                "attr_first_name": self.first_name_attr,
                "attr_last_name": self.last_name_attr,
                "attr_username": self.username_attr,
                "attr_email": self.email_attr,
            }.items()
            if v
        }

    @property
    def config(self) -> dict[str, str]:
        # returns the config for the get_idp method
        return {
            "entity_id": self.entity_id,
            "url": self.sso_url,
            "x509cert": self.x509_cert,
        } | self.user_attribute_map

    @property
    def security_config(self) -> SamlSecurityConfig:
        mode = self._require_choice(
            field_name="requested_authn_context_mode",
            value=self.requested_authn_context_mode,
            choices=self.RequestedAuthnContextMode,
        )
        if mode == self.RequestedAuthnContextMode.DISABLED:
            return {"requestedAuthnContext": False}

        comparison = cast(
            RequestedAuthnContextComparisonValue,
            REQUESTED_AUTHN_CONTEXT_COMPARISON_MAP[
                self._require_choice(
                    field_name="requested_authn_context_comparison",
                    value=self.requested_authn_context_comparison,
                    choices=self.RequestedAuthnContextComparison,
                )
            ],
        )
        if mode == self.RequestedAuthnContextMode.PASSWORD:
            return {
                "requestedAuthnContext": True,
                "requestedAuthnContextComparison": comparison,
            }

        requested_authn_context_values, error_message = (
            self._normalize_requested_authn_context_values()
        )
        if error_message is not None:
            raise IdentityProviderConfigurationError(
                field_name="requested_authn_context_values",
                idp_name=self.label or None,
            )
        return {
            "requestedAuthnContext": requested_authn_context_values,
            "requestedAuthnContextComparison": comparison,
        }

    def _require_choice(
        self,
        *,
        field_name: str,
        value: str,
        choices: type[models.TextChoices],
    ) -> str:
        if value not in choices.values:
            raise IdentityProviderConfigurationError(
                field_name=field_name,
                idp_name=self.label or None,
            )
        return value

    def _normalize_requested_authn_context_values(
        self,
    ) -> tuple[list[str], str | None]:
        if not isinstance(self.requested_authn_context_values, list):
            return [], "Enter a JSON array of authn context class refs."

        requested_authn_context_values: list[str] = []
        for value in self.requested_authn_context_values:
            if not isinstance(value, str):
                return [], "Each requested authn context value must be a string."
            stripped_value = value.strip()
            if not stripped_value:
                return [], (
                    "Each requested authn context value must be a non-empty string."
                )
            requested_authn_context_values.append(stripped_value)

        if not requested_authn_context_values:
            return (
                [],
                "Provide at least one requested authn context value for CUSTOM mode.",
            )

        return requested_authn_context_values, None

    def x509_cert_short(self) -> str:
        """Return truncated version of X.509 certificate."""
        if not self.x509_cert:
            return ""
        return self.x509_cert[:20] + "..." + self.x509_cert[-20:]
