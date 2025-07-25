# Generated by Django 4.0.4 on 2022-07-09 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laboratory', '0002_remove_labpanelorder_asn_laborder_doc_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='labpanel',
            name='bill_item_code',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='labpanelorder',
            name='approved_by',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='labpanelorder',
            name='approved_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='labpanelorder',
            name='bill',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
