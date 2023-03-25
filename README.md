# Django Heroku Github Sync

Django app to demonstrate SAML authentication using Python Social Auth.

## Version support

This app support Django 4.1+ and Python 3.11+.

## Background

Implementing and testing SAML requires an accessible URL - this project is
designed to show an app running on Heroku that can authenticate a user
against a known Identity Provider (IdP).

This is a Django app that uses `social-auth-app-django` and
`python3-saml` to demonstrate the end to end flow.

It is designed to be deployed to Heroku, although you could test locally
with ngrok. You just need a (HTTPS) URL that the IdP can connect to.

## Configuration

Click this button to deploy to Heroku:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

You must supply three SAML settings that should be available from your test
IdP provider. If you have a Google Workspace account, that can be used - see
https://admin.google.com/ac/security/ssocert for details.

## Miscellaneous (tests, etc.)

This app is designed to be deployed, not downloaded as a package - it's not on
PyPI, it has no tests, or CI build.

## DISCLAIMER

This app demonstrate SSO using SAML2.0, which means it's _destined_ (but not
designed) to be used in security-conscious enterprise environments. It is a
**demonstration** only - it should NOT BE TRUSTED, and you do so at YOUR OWN
RISK.

**Do not deploy this in a secure environment, and do not connect it to a real IdP.**
