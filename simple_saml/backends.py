import logging
from typing import Any, cast

from social_core.backends.saml import SAMLAuth as BaseSAMLAuth, SAMLIdentityProvider

from .exceptions import (
    IdentityProviderDisabledError,
    IdentityProviderNotFoundError,
    MissingIdentityProviderNameError,
    MissingUserPermanentIdError,
)
from .models import IdentityProvider, SamlSecurityConfig

logger = logging.getLogger(__name__)


class SimpleSAMLIdentityProvider(SAMLIdentityProvider):
    """SAML identity provider with package-specific security overrides."""

    def __init__(
        self,
        backend: BaseSAMLAuth,
        name: str,
        *,
        security_config: SamlSecurityConfig | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(backend=backend, name=name, **kwargs)
        self.security_config = security_config or {}


class SimpleSAMLAuth(BaseSAMLAuth):
    """Subclass of SAMLAuth that stores the IdP info in a model."""

    def get_idp(self, idp_name: str | None) -> SimpleSAMLIdentityProvider:
        if idp_name is None:
            raise MissingIdentityProviderNameError()
        try:
            idp = IdentityProvider.objects.get(label=idp_name)
        except IdentityProvider.DoesNotExist as ex:
            raise IdentityProviderNotFoundError(idp_name=idp_name) from ex
        if not idp.is_enabled:
            raise IdentityProviderDisabledError(idp_name=idp_name)
        return SimpleSAMLIdentityProvider(
            backend=self,
            name=idp_name,
            security_config=idp.security_config,
            **idp.config,
        )

    def generate_saml_config(
        self,
        idp: SAMLIdentityProvider | None = None,
    ) -> dict[str, object]:
        config = cast(dict[str, object], super().generate_saml_config(idp))
        if isinstance(idp, SimpleSAMLIdentityProvider):
            cast(dict[str, object], config["security"]).update(idp.security_config)
        return config

    def get_user_id(self, details: dict, response: dict) -> str:
        """Return the permanent user id from the response."""
        try:
            return super().get_user_id(details, response)
        except KeyError as ex:
            response_keys = tuple(sorted(response.keys()))
            logger.warning(
                "Error getting user_permanent_id from response. "
                "Available response keys: %s",
                response_keys,
                exc_info=True,
            )
            raise MissingUserPermanentIdError(response_keys=response_keys) from ex
