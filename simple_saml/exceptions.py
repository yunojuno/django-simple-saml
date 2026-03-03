from __future__ import annotations


class SamlException(Exception):
    """Base class for all exceptions raised by this library."""


class IdentityProviderError(SamlException):
    """Base class for Identity Provider related errors."""

    def __init__(self, message: str, *, idp_name: str | None = None) -> None:
        self.idp_name = idp_name
        super().__init__(message)


class MissingIdentityProviderNameError(IdentityProviderError):
    """Raised when a SAML authentication request does not provide an IdP name."""

    def __init__(self) -> None:
        super().__init__("Identity provider name is required.")


class IdentityProviderUnavailableError(IdentityProviderError):
    """Raised when an IdP cannot be used for authentication."""

    def __init__(self, *, idp_name: str, reason: str) -> None:
        self.reason = reason
        super().__init__("Identity provider is unavailable.", idp_name=idp_name)


class IdentityProviderNotFoundError(IdentityProviderUnavailableError):
    """Raised when the requested IdP label does not exist."""

    def __init__(self, *, idp_name: str) -> None:
        super().__init__(idp_name=idp_name, reason="not_found")


class IdentityProviderDisabledError(IdentityProviderUnavailableError):
    """Raised when the requested IdP exists but is disabled."""

    def __init__(self, *, idp_name: str) -> None:
        super().__init__(idp_name=idp_name, reason="disabled")


class IdentityProviderConfigurationError(SamlException):
    """Raised when required Identity Provider configuration is missing."""

    def __init__(self, *, field_name: str, idp_name: str | None = None) -> None:
        self.field_name = field_name
        self.idp_name = idp_name
        if idp_name:
            message = (
                "Identity provider configuration is invalid: "
                f"{field_name} is required for '{idp_name}'."
            )
        else:
            message = (
                "Identity provider configuration is invalid: "
                f"{field_name} is required."
            )
        super().__init__(message)


class MissingUserPermanentIdError(SamlException):
    """Raised when the SAML response has no permanent user identifier."""

    def __init__(self, *, response_keys: tuple[str, ...]) -> None:
        self.response_keys = response_keys
        super().__init__("SAML response is missing the permanent user id attribute.")


class MetadataException(SamlException):
    """Raised when metadata XML cannot be generated."""

    def __init__(self, *, backend_errors: tuple[str, ...] = ()) -> None:
        self.backend_errors = backend_errors
        super().__init__("Error loading SAML backend.")


class MetadataViewException(SamlException):
    """Raised when the metadata view cannot return XML."""

    def __init__(self) -> None:
        super().__init__("Error generating metadata XML.")
