# Django Simple SAML

Django app to manage SAML Identity Providers

## Version support

This app support Django 3.2+ and Python 3.8+.

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

## Local install & setup

If you are having problems installing `xmlsec` locally, try this:
https://github.com/xmlsec/python-xmlsec/issues/254

## DISCLAIMER

The demo app demonstrate SSO using SAML2.0, which means it's _destined_
(but not designed) to be used in security-conscious enterprise
environments. It is a **demonstration** only - it should NOT BE TRUSTED,
and you do so at YOUR OWN RISK.

**Do not deploy the demo into a secure environment, and do not connect
it to a real IdP.**
