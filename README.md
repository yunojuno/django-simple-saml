# Django Simple SAML

Django app to manage SAML Identity Providers

## Version support

This app supports Python 3.12+ and Django 5.2-6.0.

## Background

This library builds on top of `social-auth-app-django` and
`python3-saml`, which together handle the heavy lifting of a SAML
authentication flow. It assumes that you are building a service that
will act as the Service Provider (SP) in the flow, and that you will be
integrating with a number of external Identity Providers (IdP) for user
authentication.

The core change to those libraries that this package adds is a new
`SAMLAuth` backend called `SimpleSAMLAuth` that reads in IdP data from a
model (i.e. the database) rather than using the settings config dict
`SOCIAL_AUTH_SAML_ENABLED_IDPS`.

The reason for this is to make it easy to update / test new IdPs on a
live environment without having to deploy. If you are running a platform
that offers SSO to clients as a feature, having to embed their IdP
details in the settings (which also requires a redeployment) isn't a
practical option.

The IdP data is input via the Django admin site.

## Settings

This package relies on the existing `python-social-auth` settings. See
their documentation for details, or refer to the `demo.settings.base`
module for an example.

## Configuration

Click this button to deploy to Heroku:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

You must supply three SAML settings that should be available from your
test IdP provider. If you have a Google Workspace account, that can be
used - see https://admin.google.com/ac/security/ssocert for details.

## IdentityProvider model

`django-simple-saml` stores each SAML Identity Provider in
`simple_saml.models.IdentityProvider`.

The existing IdP metadata and attribute mapping fields still populate the
`social-auth-app-django` / `python-social-auth` IdP configuration.

Requested authentication context is configured separately per IdP via
these fields:

- `requested_authn_context_mode`
- `requested_authn_context_values`
- `requested_authn_context_comparison`

This configuration is merged into the generated `python3-saml`
`security` settings when the AuthnRequest is built.

## RequestedAuthnContext configuration

By default, `django-simple-saml` now disables
`RequestedAuthnContext` for every `IdentityProvider`.

That means new and existing `IdentityProvider` rows behave like:

- `security["requestedAuthnContext"] = False`

This overrides the upstream `python3-saml` default, which would
otherwise send the password-based context implicitly.

### Modes

#### `DISABLED`

Do not send `RequestedAuthnContext`.

Equivalent `python3-saml` security config:

- `requestedAuthnContext = False`

#### `PASSWORD`

Send the upstream password-based context:

- `urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport`

Equivalent `python3-saml` security config:

- `requestedAuthnContext = True`
- `requestedAuthnContextComparison = <configured comparison>`

This preserves the previous package behavior for IdPs that still require
it, but it must now be enabled explicitly per `IdentityProvider`.

#### `CUSTOM`

Send one or more explicit AuthnContext class refs.

Equivalent `python3-saml` security config:

- `requestedAuthnContext = <list of configured values>`
- `requestedAuthnContextComparison = <configured comparison>`

`CUSTOM` requires at least one value in
`requested_authn_context_values`.

### Supported comparison values

`requested_authn_context_comparison` supports:

- `exact`
- `minimum`
- `maximum`
- `better`

### Example

```python
from simple_saml.models import IdentityProvider

IdentityProvider.objects.create(
    label="acme",
    provider="Acme Okta",
    entity_id="https://acme.okta.example/app/sso/saml/metadata",
    sso_url="https://acme.okta.example/app/sso/saml",
    x509_cert="MIIC...",
    user_permanent_id_attr="email",
    requested_authn_context_mode=IdentityProvider.RequestedAuthnContextMode.CUSTOM,
    requested_authn_context_values=[
        "urn:example:loa:2",
        "urn:example:loa:3",
    ],
    requested_authn_context_comparison=(
        IdentityProvider.RequestedAuthnContextComparison.MINIMUM
    ),
)
```

## Admin support

The Django admin exposes the RequestedAuthnContext fields directly on the
`IdentityProvider` form.

Validation rules:

- `CUSTOM` requires at least one authn context value.
- `DISABLED` and `PASSWORD` ignore stored custom values.
- `requested_authn_context_comparison` is restricted to the supported
  `python3-saml` values.
