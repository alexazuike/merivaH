from django.contrib import admin
from .models import Clinic, Encounter, EncounterTemplate

# Register your models here.
admin.site.register(Clinic)
admin.site.register(Encounter)
admin.site.register(EncounterTemplate)
