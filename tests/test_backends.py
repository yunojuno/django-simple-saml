from __future__ import annotations

import pytest
from social_core.backends.saml import SAMLAuth as BaseSAMLAuth

from simple_saml.backends import SimpleSAMLAuth
from simple_saml.exceptions import (
    IdentityProviderDisabledError,
    IdentityProviderNotFoundError,
    MissingIdentityProviderNameError,
    MissingUserPermanentIdError,
)
from simple_saml.models import IdentityProvider


class TestSimpleSAMLAuth:
    def test_get_idp_requires_name(self) -> None:
        backend = SimpleSAMLAuth.__new__(SimpleSAMLAuth)
        with pytest.raises(MissingIdentityProviderNameError):
            backend.get_idp(None)

    def test_get_idp_raises_not_found_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        backend = SimpleSAMLAuth.__new__(SimpleSAMLAuth)

        def _missing_idp(*args: object, **kwargs: object) -> IdentityProvider:
            raise IdentityProvider.DoesNotExist

        monkeypatch.setattr(IdentityProvider.objects, "get", _missing_idp)

        with pytest.raises(IdentityProviderNotFoundError) as ex:
            backend.get_idp("acme")
        assert ex.value.idp_name == "acme"
        assert str(ex.value) == "Identity provider is unavailable."

    def test_get_idp_raises_disabled_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        backend = SimpleSAMLAuth.__new__(SimpleSAMLAuth)
        provider = IdentityProvider(
            label="acme",
            entity_id="https://acme.example/idp",
            sso_url="https://acme.example/sso",
            x509_cert="CERT",
            user_permanent_id_attr="uid",
            is_enabled=False,
        )

        def _disabled_idp(*args: object, **kwargs: object) -> IdentityProvider:
            return provider

        monkeypatch.setattr(IdentityProvider.objects, "get", _disabled_idp)

        with pytest.raises(IdentityProviderDisabledError) as ex:
            backend.get_idp("acme")
        assert ex.value.idp_name == "acme"
        assert str(ex.value) == "Identity provider is unavailable."

    def test_get_idp_unavailable_errors_share_public_message(self) -> None:
        not_found = IdentityProviderNotFoundError(idp_name="acme")
        disabled = IdentityProviderDisabledError(idp_name="acme")
        assert str(not_found) == str(disabled) == "Identity provider is unavailable."

    def test_get_user_id_wraps_missing_attribute_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        backend = SimpleSAMLAuth.__new__(SimpleSAMLAuth)

        def _missing_permanent_id(
            self: BaseSAMLAuth,
            details: dict,
            response: dict,
        ) -> str:
            raise KeyError("attr_user_permanent_id")

        monkeypatch.setattr(BaseSAMLAuth, "get_user_id", _missing_permanent_id)

        with pytest.raises(MissingUserPermanentIdError) as ex:
            backend.get_user_id({}, {"email": "user@example.com", "first_name": "Ada"})

        assert ex.value.response_keys == ("email", "first_name")
