# Generated by Django 4.0.4 on 2022-07-09 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0002_patient_email_alter_patient_home_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='payment_scheme',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='patient',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]
