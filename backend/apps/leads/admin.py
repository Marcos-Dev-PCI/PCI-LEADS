from django.contrib import admin
from .models import Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "email",
        "phone",
        "city",
        "state",
        "created_at",
    )
    search_fields = ("name", "company", "email", "city", "state")
