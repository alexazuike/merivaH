from django.db import models


# Create your models here.
class Facility(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.JSONField()
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    lga = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField(max_length=254)
    facility_code = models.CharField(max_length=254)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Facilities"

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=255)
    display_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.display_name
