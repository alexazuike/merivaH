from config.preferences import (
    APP_PREFERENCES,
    PreferencesStruct,
    AppPreferencesDataTypes,
)
from api.apps.core.models import AppPreferences as PreferencesModel

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "setup all default preferences"

    def _get_create_app_preferences(self, preferences_struct: PreferencesStruct):
        if not preferences_struct.env:
            title = preferences_struct.name.upper().replace("_", " ")
            preferences, created = PreferencesModel.objects.get_or_create(
                title=title,
                category=preferences_struct.category,
                defaults=preferences_struct.to_dict(),
            )
            data_type = AppPreferencesDataTypes.get_type(preferences.type)
            return data_type(preferences.value)

    def handle(self, *args, **options):
        for preferences in APP_PREFERENCES:
            preference = self._get_create_app_preferences(
                preferences_struct=preferences
            )
            self.stdout.write(self.style.SUCCESS(preference))
