from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Salutation)
admin.site.register(models.Gender)
admin.site.register(models.Country)
admin.site.register(models.State)
admin.site.register(models.LGA)
admin.site.register(models.District)
admin.site.register(models.Occupation)
admin.site.register(models.MaritalStatus)
admin.site.register(models.Religion)
admin.site.register(models.Template)
admin.site.register(models.Diagnosis)
admin.site.register(models.ServiceArm)
admin.site.register(models.AppPreferences)
