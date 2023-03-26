from django.db import models


class IdentityProvider(models.Model):
    """Class to store the Identity Provider metadata."""

    name = models.CharField(max_length=255)
    entity_id = models.CharField(max_length=255)
    sso_url = models.CharField(max_length=255)
    x509cert = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    @property
    def config(self) -> dict[str, str]:
        # returns the config for the get_idp method
        retval = {
            "entity_id": self.entity_id,
            "url": self.sso_url,
            "x509cert": self.x509cert,
        }
        retval.update(self.metadata)
        return retval
