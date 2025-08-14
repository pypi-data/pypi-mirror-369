from enum import Enum


class DataMigrationStatus(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"

    @classmethod
    def choices(cls):
        return [(i.name, i.value) for i in cls]
