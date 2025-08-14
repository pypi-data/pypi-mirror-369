from django.contrib import admin

from .models import ConfirmationState


@admin.register(ConfirmationState)
class ConfirmationStateAdmin(admin.ModelAdmin):
    list_display = 'id', 'code', 'confirmed_at', 'used_at', 'created_at', 'updated_at',
    date_hierarchy = 'created_at'
    list_filter = 'confirmed_at', 'used_at', 'created_at', 'updated_at'
    search_fields = 'code', 'meta',
    ordering = ('-created_at', )
    readonly_fields = 'created_at', 'updated_at',
