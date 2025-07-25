# Generated by Django 4.0.4 on 2022-09-08 12:29

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0004_alter_patient_options_patient_deposit_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='PatientFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('path', models.CharField(blank=True, max_length=256, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.JSONField(default=dict)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.JSONField(default=dict)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patient.patient')),
            ],
            options={
                'verbose_name_plural': 'Patient Files',
            },
        ),
    ]
