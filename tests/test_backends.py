from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pytest
from onelogin.saml2.constants import OneLogin_Saml2_Constants
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from social_core.backends.saml import SAMLAuth as BaseSAMLAuth

from simple_saml.backends import SimpleSAMLAuth
from simple_saml.exceptions import (
    IdentityProviderDisabledError,
    IdentityProviderNotFoundError,
    MissingIdentityProviderNameError,
    MissingUserPermanentIdError,
)
from simple_saml.models import IdentityProvider


class FakeStrategy:
    SESSION_SAVE_KEY = "session_key"

    def request_data(self) -> dict[str, str]:
        return {"idp": "acme"}

    def absolute_uri(self, path: str | None = None) -> str:
        return f"https://sp.example{path or ''}"

    def setting(
        self,
        name: str,
        default: object = None,
        backend: object | None = None,
    ) -> object:
        settings = {
            "SP_ENTITY_ID": "https://sp.example/metadata/",
            "SP_PUBLIC_CERT": "",
            "SP_PRIVATE_KEY": "",
            "ORG_INFO": {
                "en-US": {
                    "name": "example",
                    "displayname": "Example",
                    "url": "https://sp.example",
                }
            },
            "TECHNICAL_CONTACT": {
                "givenName": "Tech",
                "emailAddress": "tech@example.com",
            },
            "SUPPORT_CONTACT": {
                "givenName": "Support",
                "emailAddress": "support@example.com",
            },
            "SECURITY_CONFIG": {},
            "SP_EXTRA": {},
        }
        return settings.get(name, default)

    def request_is_secure(self) -> bool:
        return True

    def request_host(self) -> str:
        return "sp.example"

    def request_path(self) -> str:
        return "/login/saml/"

    def request_get(self) -> dict[str, str]:
        return {"idp": "acme"}

    def request_post(self) -> dict[str, str]:
        return {}

    def get_session_id(self) -> None:
        return None


def build_backend() -> SimpleSAMLAuth:
    return SimpleSAMLAuth(strategy=FakeStrategy(), redirect_uri="/complete/saml/")


def build_provider(**overrides: object) -> IdentityProvider:
    provider = IdentityProvider(
        label="acme",
        entity_id="https://acme.example/idp",
        sso_url="https://acme.example/sso",
        x509_cert="CERT",
        user_permanent_id_attr="uid",
        **overrides,
    )
    provider.clean()
    return provider


def decode_saml_request_from_url(url: str) -> str:
    query = parse_qs(urlparse(url).query)
    return OneLogin_Saml2_Utils.decode_base64_and_inflate(
        query["SAMLRequest"][0]
    ).decode()


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

    def test_generate_saml_config_uses_disabled_authn_context_by_default(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        provider = build_provider()
        backend = build_backend()
        monkeypatch.setattr(IdentityProvider.objects, "get", lambda **kwargs: provider)

        config = backend.generate_saml_config(backend.get_idp(provider.label))

        assert config["security"]["requestedAuthnContext"] is False
        assert "requestedAuthnContextComparison" not in config["security"]

    def test_generate_saml_config_password_mode_uses_configured_comparison(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        provider = build_provider(
            requested_authn_context_mode=(
                IdentityProvider.RequestedAuthnContextMode.PASSWORD
            ),
            requested_authn_context_comparison=(
                IdentityProvider.RequestedAuthnContextComparison.MINIMUM
            ),
        )
        backend = build_backend()
        monkeypatch.setattr(IdentityProvider.objects, "get", lambda **kwargs: provider)

        config = backend.generate_saml_config(backend.get_idp(provider.label))

        assert config["security"]["requestedAuthnContext"] is True
        assert config["security"]["requestedAuthnContextComparison"] == "minimum"

    def test_generate_saml_config_custom_mode_passes_multiple_values(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        provider = build_provider(
            requested_authn_context_mode=IdentityProvider.RequestedAuthnContextMode.CUSTOM,
            requested_authn_context_comparison=(
                IdentityProvider.RequestedAuthnContextComparison.BETTER
            ),
            requested_authn_context_values=["urn:example:loa:2", "urn:example:loa:3"],
        )
        backend = build_backend()
        monkeypatch.setattr(IdentityProvider.objects, "get", lambda **kwargs: provider)

        config = backend.generate_saml_config(backend.get_idp(provider.label))

        assert config["security"]["requestedAuthnContext"] == [
            "urn:example:loa:2",
            "urn:example:loa:3",
        ]
        assert config["security"]["requestedAuthnContextComparison"] == "better"

    def test_auth_url_omits_requested_authn_context_when_disabled(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            IdentityProvider.objects,
            "get",
            lambda **kwargs: build_provider(),
        )
        backend = build_backend()

        auth_url = backend.auth_url()
        saml_request_xml = decode_saml_request_from_url(auth_url)

        assert "RequestedAuthnContext" not in saml_request_xml

    def test_auth_url_password_mode_matches_password_protected_transport(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            IdentityProvider.objects,
            "get",
            lambda **kwargs: build_provider(
                requested_authn_context_mode=(
                    IdentityProvider.RequestedAuthnContextMode.PASSWORD
                ),
                requested_authn_context_comparison=(
                    IdentityProvider.RequestedAuthnContextComparison.EXACT
                ),
            ),
        )
        backend = build_backend()

        auth_url = backend.auth_url()
        saml_request_xml = decode_saml_request_from_url(auth_url)

        assert 'RequestedAuthnContext Comparison="exact"' in saml_request_xml
        assert OneLogin_Saml2_Constants.AC_PASSWORD_PROTECTED in saml_request_xml

    def test_auth_url_custom_mode_includes_all_requested_authn_context_values(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            IdentityProvider.objects,
            "get",
            lambda **kwargs: build_provider(
                requested_authn_context_mode=(
                    IdentityProvider.RequestedAuthnContextMode.CUSTOM
                ),
                requested_authn_context_comparison=(
                    IdentityProvider.RequestedAuthnContextComparison.MAXIMUM
                ),
                requested_authn_context_values=[
                    "urn:example:loa:2",
                    "urn:example:loa:3",
                ],
            ),
        )
        backend = build_backend()

        auth_url = backend.auth_url()
        saml_request_xml = decode_saml_request_from_url(auth_url)

        assert 'RequestedAuthnContext Comparison="maximum"' in saml_request_xml
        assert "urn:example:loa:2" in saml_request_xml
        assert "urn:example:loa:3" in saml_request_xml
