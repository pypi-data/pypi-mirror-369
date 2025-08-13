import importlib
import time

from dm.managers.dm.core import DataMigrationManager
from django.conf import settings

from dm.utils.logging import logger


class DataMigrationRunner:
    @classmethod
    def _get_base_list_of_task_classes(cls):
        base_task_classes = []
        try:
            base_task_classes = settings.DATA_MIGRATION_REGISTRY
        except Exception as e:
            logger.warning(
                f"Exception occurred while trying to get base list of data migration tasks - {str(e)}"
            )
        return base_task_classes

    @classmethod
    def _get_retry_config(cls):
        total_retries, retry_delay_in_seconds = 5, 5
        try:
            total_retries = settings.DATA_MIGRATION_TOTAL_RETRIES
            retry_delay_in_seconds = settings.DATA_MIGRATION_RETRY_DELAY_IN_SECONDS
        except Exception:
            pass
        return total_retries, retry_delay_in_seconds

    def get_all_dm_tasks_classes(self):
        return self._get_base_list_of_task_classes()

    def get_retry_config(self):
        return self._get_retry_config()

    @classmethod
    def import_and_get_class(cls, task_class_string):
        full_class_path = task_class_string.split(".")
        class_name = full_class_path[-1]
        class_path = ".".join(full_class_path[:-1])
        module_containing_class = importlib.import_module(name=class_path)
        task_class = getattr(module_containing_class, class_name)
        return task_class

    def _run(self):
        all_task_classes_strings, failure_recorded = (
            self.get_all_dm_tasks_classes(),
            False,
        )
        for task_class_string in all_task_classes_strings:
            task_class = self.import_and_get_class(task_class_string=task_class_string)
            dm_manager = DataMigrationManager(task_class=task_class)
            success = dm_manager.run()
            if success is False:
                failure_recorded = True
        return failure_recorded

    def run(self):
        total_retries, retry_delay_in_seconds = self.get_retry_config()
        attempt = 1
        while attempt <= total_retries:
            time.sleep(retry_delay_in_seconds * (attempt - 1))
            logger.info(f"Running Data Migration tasks - attempt {attempt}")
            failure = self._run()
            if not failure:
                break
            logger.info(
                f"One or more Data Migration Tasks failed for attempt {attempt}. "
                f"Attempting to retrying Data Migration tasks..."
            )
            attempt += 1

        if attempt > total_retries:
            logger.error(
                f"Data Migration tasks failed after {total_retries} attempts. "
                f"Please check the logs for more details."
            )
            return False

        logger.info(
            f"Data Migration tasks completed successfully in {attempt} attempt(s)."
        )
        return True
