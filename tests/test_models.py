import pytest

from simple_saml.models import IdentityProvider


class TestIdentityProvider:
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
        with pytest.raises(ValueError):
            provider.user_attribute_map
