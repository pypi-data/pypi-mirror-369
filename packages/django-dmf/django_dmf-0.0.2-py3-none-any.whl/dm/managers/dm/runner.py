import importlib

# from core.utils.logging import logger
from dm.managers.dm.core import DataMigrationManager
from django.conf import settings


class DataMigrationRunner:
    @classmethod
    def _get_base_list_of_task_classes(cls):
        base_task_classes = []
        try:
            base_task_classes = settings.DATA_MIGRATION_REGISTRY
        except Exception:
            pass
            # logger.info(
            #     f"Exception occurred while trying to get base list of data migration tasks - {str(e)}"
            # )
        return base_task_classes

    def get_all_dm_tasks_classes(self):
        return self._get_base_list_of_task_classes()

    @classmethod
    def import_and_get_class(cls, task_class_string):
        full_class_path = task_class_string.split(".")
        class_name = full_class_path[-1]
        class_path = ".".join(full_class_path[:-1])
        module_containing_class = importlib.import_module(name=class_path)
        task_class = getattr(module_containing_class, class_name)
        return task_class

    def run(self):
        all_task_classes_strings = self.get_all_dm_tasks_classes()
        for task_class_string in all_task_classes_strings:
            task_class = self.import_and_get_class(task_class_string=task_class_string)
            dm_manager = DataMigrationManager(task_class=task_class)
            dm_manager.run()
