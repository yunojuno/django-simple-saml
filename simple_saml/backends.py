import logging

from social_core.backends.saml import SAMLAuth as BaseSAMLAuth, SAMLIdentityProvider

from .exceptions import (
    IdentityProviderDisabledError,
    IdentityProviderNotFoundError,
    MissingIdentityProviderNameError,
    MissingUserPermanentIdError,
)
from .models import IdentityProvider

logger = logging.getLogger(__name__)


class SimpleSAMLAuth(BaseSAMLAuth):
    """Subclass of SAMLAuth that stores the IdP info in a model."""

    def get_idp(self, idp_name: str | None) -> SAMLIdentityProvider:
        if idp_name is None:
            raise MissingIdentityProviderNameError()
        try:
            idp = IdentityProvider.objects.get(label=idp_name)
        except IdentityProvider.DoesNotExist as ex:
            raise IdentityProviderNotFoundError(idp_name=idp_name) from ex
        if not idp.is_enabled:
            raise IdentityProviderDisabledError(idp_name=idp_name)
        return SAMLIdentityProvider(backend=self, name=idp_name, **idp.config)

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
