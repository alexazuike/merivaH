from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.LabPanel)
admin.site.register(models.LabObservation)
admin.site.register(models.LabSpecimen)
admin.site.register(models.LabUnit)
