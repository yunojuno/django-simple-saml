import pytest
from django.core.exceptions import ValidationError

from simple_saml.exceptions import IdentityProviderConfigurationError
from simple_saml.models import IdentityProvider


class TestIdentityProvider:
    def test_requested_authn_context_defaults_to_disabled(self) -> None:
        provider = IdentityProvider()
        assert (
            provider.requested_authn_context_mode
            == IdentityProvider.RequestedAuthnContextMode.DISABLED
        )
        assert provider.requested_authn_context_values == []
        assert (
            provider.requested_authn_context_comparison
            == IdentityProvider.RequestedAuthnContextComparison.EXACT
        )
        assert provider.security_config == {"requestedAuthnContext": False}

    def test_user_attr_map(self) -> None:
        provider = IdentityProvider(
            user_permanent_id_attr="uid",
            first_name_attr="first_name",
            last_name_attr="last_name",
            email_attr="email",
            username_attr="username",
        )
        assert provider.user_attribute_map == {
            "attr_user_permanent_id": "uid",
            "attr_first_name": "first_name",
            "attr_last_name": "last_name",
            "attr_email": "email",
            "attr_username": "username",
        }

    def test_user_attr_map_id_only(self) -> None:
        provider = IdentityProvider(user_permanent_id_attr="uid")
        assert provider.user_attribute_map == {"attr_user_permanent_id": "uid"}

    def test_user_attr_map_empty(self) -> None:
        provider = IdentityProvider()
        with pytest.raises(IdentityProviderConfigurationError):
            provider.user_attribute_map

    def test_security_config_password_mode(self) -> None:
        provider = IdentityProvider(
            requested_authn_context_mode=IdentityProvider.RequestedAuthnContextMode.PASSWORD,
            requested_authn_context_comparison=(
                IdentityProvider.RequestedAuthnContextComparison.MINIMUM
            ),
        )
        assert provider.security_config == {
            "requestedAuthnContext": True,
            "requestedAuthnContextComparison": "minimum",
        }

    def test_requested_authn_context_comparison_values_are_uppercase_in_storage(
        self,
    ) -> None:
        assert IdentityProvider.RequestedAuthnContextComparison.EXACT == "EXACT"
        assert IdentityProvider.RequestedAuthnContextComparison.MINIMUM == "MINIMUM"
        assert IdentityProvider.RequestedAuthnContextComparison.MAXIMUM == "MAXIMUM"
        assert IdentityProvider.RequestedAuthnContextComparison.BETTER == "BETTER"

    def test_security_config_custom_mode(self) -> None:
        provider = IdentityProvider(
            requested_authn_context_mode=IdentityProvider.RequestedAuthnContextMode.CUSTOM,
            requested_authn_context_comparison=(
                IdentityProvider.RequestedAuthnContextComparison.BETTER
            ),
            requested_authn_context_values=["urn:example:loa:2", "urn:example:loa:3"],
        )
        assert provider.security_config == {
            "requestedAuthnContext": ["urn:example:loa:2", "urn:example:loa:3"],
            "requestedAuthnContextComparison": "better",
        }

    def test_clean_requires_custom_values(self) -> None:
        provider = IdentityProvider(
            requested_authn_context_mode=IdentityProvider.RequestedAuthnContextMode.CUSTOM,
            requested_authn_context_values=[],
        )
        with pytest.raises(ValidationError) as ex:
            provider.clean()

        assert ex.value.message_dict == {
            "requested_authn_context_values": [
                "Provide at least one requested authn context value for CUSTOM mode."
            ]
        }

    def test_clean_rejects_non_string_custom_values(self) -> None:
        provider = IdentityProvider(
            requested_authn_context_mode=IdentityProvider.RequestedAuthnContextMode.CUSTOM,
            requested_authn_context_values=["urn:example:loa:2", 123],
        )
        with pytest.raises(ValidationError) as ex:
            provider.clean()

        assert ex.value.message_dict == {
            "requested_authn_context_values": [
                "Each requested authn context value must be a string."
            ]
        }

    def test_non_custom_modes_ignore_stored_custom_values(self) -> None:
        provider = IdentityProvider(
            requested_authn_context_mode=IdentityProvider.RequestedAuthnContextMode.DISABLED,
            requested_authn_context_values=["urn:example:loa:2"],
        )
        assert provider.security_config == {"requestedAuthnContext": False}
