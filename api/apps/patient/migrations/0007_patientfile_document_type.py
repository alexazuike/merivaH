# Generated by Django 4.0.4 on 2022-12-09 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_documenttype_alter_apppreferences_category_and_more'),
        ('patient', '0006_patient_service_arm_patient_service_arm_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientfile',
            name='document_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.documenttype'),
        ),
    ]
