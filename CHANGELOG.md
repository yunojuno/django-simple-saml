# Changelog

All notable changes to this project are documented in this file.

## [2.0.0] - 2026-03-25

### Breaking changes

- `RequestedAuthnContext` is no longer sent in SAML AuthnRequests by default. To preserve the previous behaviour, set `requested_authn_context_mode` to `PASSWORD` on each of your existing `IdentityProvider` records.

### Added

- Per-IdP `RequestedAuthnContext` configuration via three new fields on `IdentityProvider`:
  - `requested_authn_context_mode` — choose between `DISABLED` (default), `PASSWORD` (PasswordProtectedTransport), or `CUSTOM` (arbitrary AuthnContextClassRef URIs).
  - `requested_authn_context_values` — JSON list of custom AuthnContextClassRef values (used in `CUSTOM` mode).
  - `requested_authn_context_comparison` — comparison operator (`exact`, `minimum`, `maximum`, `better`) passed to python3-saml.
- `IdentityProvider.security_config` property that returns python3-saml-compatible security settings for the configured authn context.
- `SimpleSAMLIdentityProvider` subclass of `SAMLIdentityProvider` that carries per-IdP security config.
- `SimpleSAMLAuth.generate_saml_config()` override that merges IdP-level security settings into the SAML config.
- Model-level validation (`clean()`) ensuring `CUSTOM` mode has at least one valid string value.
- Admin UI section for managing RequestedAuthnContext settings.

### Fixed

- Tox environment names in GitHub Actions workflow.

## [1.0.0] - 2026-03-03

### Breaking changes

- `SimpleSAMLAuth.get_idp(None)` now raises `MissingIdentityProviderNameError` instead of `ValueError`.
- `SimpleSAMLAuth.get_idp(<unknown>)` now raises `IdentityProviderNotFoundError` instead of `ValueError`.
- `SimpleSAMLAuth.get_idp(<disabled>)` now raises `IdentityProviderDisabledError` instead of `ValueError`.
- `SimpleSAMLAuth.get_user_id(...)` now raises `MissingUserPermanentIdError` instead of propagating `KeyError` when the permanent ID attribute is missing.
- `IdentityProvider.user_attribute_map` now raises `IdentityProviderConfigurationError` instead of `ValueError` when `user_permanent_id_attr` is missing.
- `saml_metadata_view` now raises `MetadataViewException` instead of generic `Exception`.
- `get_saml_metadata(...)` now raises `MetadataException` with `backend_errors` context.

### Added

- New typed exception hierarchy in `simple_saml.exceptions`:
  - `SamlException`
  - `IdentityProviderError`
  - `IdentityProviderUnavailableError`
  - `MissingIdentityProviderNameError`
  - `IdentityProviderNotFoundError`
  - `IdentityProviderDisabledError`
  - `IdentityProviderConfigurationError`
  - `MissingUserPermanentIdError`
  - `MetadataException`
  - `MetadataViewException`

### Security and behavior changes

- Identity provider lookup now uses the same public error message (`"Identity provider is unavailable."`) for both "not found" and "disabled" cases to avoid leaking IdP state details in user-facing responses.

### Upgrade guide

Update exception handling from message-based checks to class-based checks.

- Before:
  - Catch `ValueError` for IdP lookup failures.
  - Catch `KeyError` for missing `attr_user_permanent_id`.
  - Catch generic `Exception` around metadata view generation.
- After:
  - Catch `MissingIdentityProviderNameError` for missing IdP parameter.
  - Catch `IdentityProviderUnavailableError` (or its subclasses) for missing/disabled IdP.
  - Catch `MissingUserPermanentIdError` for missing permanent user ID.
  - Catch `IdentityProviderConfigurationError` for invalid IdP model configuration.
  - Catch `MetadataException` and/or `MetadataViewException` for metadata failures.

If you need to distinguish why an IdP is unavailable, inspect the concrete type (`IdentityProviderNotFoundError` vs `IdentityProviderDisabledError`) or `reason` attribute on `IdentityProviderUnavailableError`.
