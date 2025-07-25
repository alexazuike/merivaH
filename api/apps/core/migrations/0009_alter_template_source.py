# Generated by Django 4.0.4 on 2023-02-13 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_documenttype_alter_apppreferences_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='template',
            name='source',
            field=models.CharField(choices=[('ENCOUNTERS', 'Encounter'), ('IMAGING', 'Imaging'), ('LABORATORY', 'Laboratory'), ('INVENTORY', 'Inventory'), ('PHARMACY', 'Pharmacy'), ('NURSING', 'Nursing'), ('FINANCE', 'Finance'), ('MESSAGING', 'Messaging')], max_length=128),
        ),
    ]
