from enum import Enum

from django.contrib.auth.models import User

from api.includes.utils import is_table_exist
from config import preferences


class EncounterStatus(str, Enum):
    NEW = "NEW"
    NS = "NS"
    DS = "DS"

    def __str__(self):
        return self.value


def generate_encounter_id():
    from api.apps.encounters.models import Encounter

    config = preferences.AppPreferences()
    serial_no = 1
    if is_table_exist("encounters_encounter"):
        if Encounter.objects.count() > 0:
            last_encounter = Encounter.objects.latest("id")
            if last_encounter is not None:
                serial_no = last_encounter.id + 1
    serial_no = str(serial_no).zfill(6)
    unique_id = f"{config.encounter_id_prefix_code}{serial_no}"
    return unique_id


def has_encounter_status_perm(user: User, status: str):
    if status.casefold() == str(EncounterStatus.NEW).casefold():
        return user.has_perm("encounters.add_encounter") or user.has_perm(
            "encounters.change_encounter"
        )
    if status.casefold() == str(EncounterStatus.NS).casefold():
        return user.has_perm("encounters.take_vitals") or user.has_perm(
            "encounters.change_encounter"
        )
    if status.casefold() == str(EncounterStatus.DS).casefold():
        return user.has_perm("encounters.sign_encounter") or user.has_perm(
            "encounters.change_encounter"
        )

    return False
