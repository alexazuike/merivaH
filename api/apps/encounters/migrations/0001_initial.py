# Generated by Django 4.0.4 on 2022-06-11 11:20

from django.db import migrations, models
import django.db.models.deletion
from api.apps.encounters import models as enc_models
from api.apps.encounters import utils
from api.includes import utils as lib
class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('facilities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Encounter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('encounter_id', models.CharField(default=utils.generate_encounter_id, editable=False, max_length=50, unique=True)),
                ('clinic', models.JSONField()),
                ('status', models.CharField(blank=True, max_length=200, null=True)),
                ('time_log', models.JSONField(default=lib.time_log_jsonfield_default_value)),
                ('chart', models.JSONField(default=lib.jsonfield_default_value)),
                ('provider', models.JSONField(default=lib.provider_jsonfield_default_value)),
                ('patient', models.JSONField()),
                ('is_active', models.BooleanField(default=True)),
                ('encounter_type', models.CharField(default='New', max_length=255)),
                ('encounter_datetime', models.DateTimeField(auto_now=True)),
                ('created_datetime', models.DateTimeField(auto_now_add=True)),
                ('chief_complaint', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name_plural': 'Encounters',
                'ordering': ['-created_datetime'],
            },
        ),
        migrations.CreateModel(
            name='Encounter_Type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Encounter Types',
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Status',
            },
        ),
        migrations.CreateModel(
            name='Clinic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('Department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clinics', to='facilities.department')),
            ],
            options={
                'verbose_name_plural': 'Clinics',
            },
        ),
    ]
