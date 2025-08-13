from django.contrib import admin
from dm.models import DataMigrationExecution


@admin.register(DataMigrationExecution)
class DataMigrationExecutionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "task",
        "execution_version",
        "status",
        "created_on",
        "updated_on",
    )
    ordering = ["-updated_on"]
    list_per_page = 25
    list_filter = ("status",)
    search_fields = ("id", "execution_version", "task")
