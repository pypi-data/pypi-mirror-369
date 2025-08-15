from django.contrib import admin

from .models import BillingAccount


@admin.register(BillingAccount)
class BillingAccountAdmin(admin.ModelAdmin):
    list_display = ["user", "account_number", "account_type", "balance"]
    readonly_fields = ["user", "account_number", "account_type", "balance"]
    list_filter = ["account_type"]
    search_fields = ["account_number"]

    def has_delete_permission(self, request, obj=None):
        return False
