import traceback

from django.db import transaction

# from core.utils.logging import logger


class BaseDataMigrationTask:
    def __init__(self, **kwargs):
        self.version = None

    def _run(self):
        raise NotImplementedError

    def run(self, **kwargs):
        if self.version is None:
            raise Exception(
                "Version not defined. Skipping running the data migration task."
            )

        transaction.set_autocommit(False)
        try:
            self._run()
        except Exception as e:
            # logger.info(
            #     f"Exception occurred while running the Data Migration task - {str(e)}"
            # )
            traceback.print_exc()
            transaction.rollback()
            transaction.set_autocommit(True)
            return False, str(e)
        else:
            transaction.commit()
            # logger.info("Transaction committed")
            transaction.set_autocommit(True)

        return True, None
