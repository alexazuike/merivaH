from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.Modality)
admin.site.register(models.ServiceCenter)
admin.site.register(models.ImagingObservation)
