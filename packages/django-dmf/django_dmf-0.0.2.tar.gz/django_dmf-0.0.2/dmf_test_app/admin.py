from django.contrib import admin
from dmf_test_app.models import FeatureSwitch


@admin.register(FeatureSwitch)
class FeatureSwitchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "active",
        "created_on",
        "updated_on",
    )
    ordering = ["-updated_on"]
    list_per_page = 25
    list_filter = ("active",)
    search_fields = ("id", "name")
