import uuid

from django.db import models
from dm.constants import DataMigrationStatus


class DataMigrationExecution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    task = models.CharField(max_length=500)
    execution_version = models.IntegerField()
    status = models.CharField(
        choices=DataMigrationStatus.choices(),
        default=DataMigrationStatus.IN_PROGRESS.value,
        max_length=100,
    )

    class Meta:
        unique_together = (("task", "execution_version"),)

    def __str__(self):
        return f"{self.task} - v{self.execution_version}"
