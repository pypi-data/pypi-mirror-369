from dm.tasks.dm.base import BaseDataMigrationTask
from dmf_test_app.managers.switch import FeatureSwitchManager


class FeatureSwitchDataMigrationTask(BaseDataMigrationTask):
    def __init__(self, **kwargs):
        super(FeatureSwitchDataMigrationTask, self).__init__(**kwargs)
        self.version = 1

    def _run(self):
        FeatureSwitchManager.seed_switches()
