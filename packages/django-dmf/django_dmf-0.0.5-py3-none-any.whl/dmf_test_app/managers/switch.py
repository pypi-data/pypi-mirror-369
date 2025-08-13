import csv

from dmf_test_app.constants import FEATURE_SWITCHES_FILE_PATH
from dmf_test_app.models import FeatureSwitch


class FeatureSwitchManager:
    @classmethod
    def seed_switches(cls):
        print("Loading all switches...")
        switches = list(csv.DictReader(open(FEATURE_SWITCHES_FILE_PATH)))
        for switch in switches:
            name = switch["name"]
            FeatureSwitch.objects.update_or_create(name=name, defaults=switch)

        print("Loaded all Switches.")
