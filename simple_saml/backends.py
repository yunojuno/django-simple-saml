from social_core.backends.saml import SAMLAuth as BaseSAMLAuth
from social_core.backends.saml import SAMLIdentityProvider

from .models import IdentityProvider


class SimpleSAMLAuth(BaseSAMLAuth):
    """Subclass of SAMLAuth that stores the IdP info in a model."""

    def get_idp(self, idp_name: str) -> SAMLIdentityProvider:
        idp = IdentityProvider.objects.get(label=idp_name)
        return SAMLIdentityProvider(idp_name, **idp.config)
