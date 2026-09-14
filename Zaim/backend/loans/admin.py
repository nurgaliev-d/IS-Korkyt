from django.contrib import admin

from .models import LoanApplication


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "amount",
        "term_months",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("full_name", "phone", "iin")
