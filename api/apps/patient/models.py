import datetime

from django.db import models
from django.utils import timezone

from api.includes import utils
from api.apps.core import models as core_models
from config import preferences

# Create your models here.


def generate_uhid():
    config = preferences.AppPreferences()
    serial_no = 1
    if utils.is_table_exist("patient_patient"):
        CURRENT_YEAR = str(datetime.datetime.utcnow().year)[2::]
        patients = Patient.objects.filter(uhid__contains=str(CURRENT_YEAR))
        if patients.count() > 0:
            last_patient = patients.latest("id")
            serial_no = int(last_patient.uhid[-6:]) + 1

    serial_no = str(serial_no).zfill(6)
    unique_id = f"{config.patient_prefix_code}{CURRENT_YEAR}{serial_no}"
    return unique_id


class Patient(models.Model):
    uhid = models.CharField(
        max_length=50, unique=True, editable=False, default=generate_uhid
    )
    is_baby = models.BooleanField(default=False)
    salutation = models.CharField(max_length=50, blank=True, null=True)
    firstname = models.CharField(max_length=50)
    middlename = models.CharField(max_length=50, blank=True, null=True)
    lastname = models.CharField(max_length=50)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=50)
    marital_status = models.CharField(max_length=50, null=True, blank=True)
    religion = models.CharField(max_length=50, null=True, blank=True)
    nationality = models.CharField(max_length=50, null=True, blank=True)
    state_id = models.JSONField(null=True, blank=True)
    home_address = models.JSONField(null=True, blank=True)
    next_of_kin = models.JSONField(null=True, blank=True)
    lga = models.CharField(max_length=255, blank=True, null=True)
    identity = models.JSONField(null=True, blank=True)
    service_arm = models.CharField(max_length=256, blank=True, null=True)
    service_arm_no = models.CharField(max_length=256, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    payment_scheme = models.JSONField(null=True, blank=True, default=list)
    profile_picture = models.TextField(null=True, blank=True)
    deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reserve = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Patients"
        permissions = (("patient_deposit", "Can deposit to patient"),)

    def to_dict(self):
        patient_data: dict = utils.model_to_dict(self)
        patient_data["date_of_birth"] = str(patient_data["date_of_birth"])
        patient_data["deposit"] = str(patient_data["deposit"])
        patient_data["reserve"] = str(patient_data["reserve"])
        return patient_data

    def full_name(self):
        return f"{self.firstname} {self.middlename} {self.lastname}"

    def __str__(self):
        return self.full_name()

    def add_deposit(self, amount: float):
        self.deposit += amount
        self.save()

    def send_to_reserve(self, amount: float):
        self.deposit -= amount
        self.reserve += amount
        self.save()

    def pay_from_reserve(self, amount: float):
        self.reserve -= amount
        self.save()

    def pay_from_deposit(self, amount: float):
        self.deposit -= amount
        self.save()

    def refund_to_reserve(self, amount: float):
        self.reserve += amount
        self.save()


class PatientFile(models.Model):
    title = models.CharField(max_length=256, blank=False, null=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    path = models.CharField(max_length=256, blank=True, null=True)
    document_type = models.ForeignKey(
        core_models.DocumentType, on_delete=models.CASCADE, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.JSONField(default=dict)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Patient Files"
