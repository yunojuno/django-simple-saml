from django.contrib import admin

from .models import IdentityProvider


@admin.register(IdentityProvider)
class IdentityProviderAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")
    list_display = ("name", "entity_id", "created_at", "updated_at")
