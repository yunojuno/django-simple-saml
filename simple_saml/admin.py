from django import forms
from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest

from .models import IdentityProvider


class IdentityProviderForm(forms.ModelForm):
    class Meta:
        model = IdentityProvider
        fields = "__all__"
        widgets = {
            "metadata": forms.Textarea(attrs={"rows": 10, "cols": 100}),
            "x509_cert": forms.Textarea(attrs={"rows": 10, "cols": 100}),
        }


@admin.register(IdentityProvider)
class IdentityProviderAdmin(admin.ModelAdmin):
    form = IdentityProviderForm
    readonly_fields = ("created_at", "updated_at", "sp_entity_id")
    list_display = ("label", "entity_id", "created_at", "updated_at", "is_enabled")
    fieldsets = (
        (None, {"fields": ("label", "is_enabled")}),
        ("Settings metadata (reference only)", {"fields": ("sp_entity_id",)}),
        (
            "Information provided by Identity Provider (IdP)",
            {
                "fields": ("entity_id", "sso_url", "x509_cert", "metadata"),
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Service Provider Entity ID")
    def sp_entity_id(self, _: IdentityProvider) -> str:
        return getattr(settings, "SOCIAL_AUTH_SAML_SP_ENTITY_ID", "missing")

    def save_model(
        self,
        request: HttpRequest,
        obj: IdentityProvider,
        form: IdentityProviderForm,
        change: bool,
    ) -> None:
        """Validate that the metadata contains attr_user_permanent_id."""
        if "attr_user_permanent_id" not in obj.metadata:
            raise forms.ValidationError("`attr_user_permanent_id` is a required key.")
        return super().save_model(request, obj, form, change)
