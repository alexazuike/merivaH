# Generated by Django 4.0.4 on 2022-07-09 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imaging', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ImagingUnit',
            new_name='Modality',
        ),
        migrations.RenameField(
            model_name='imagingobservation',
            old_name='img_unit',
            new_name='modality',
        ),
        migrations.RemoveField(
            model_name='imagingobservationorder',
            name='img_id',
        ),
        migrations.AddField(
            model_name='imagingobservation',
            name='bill_item_code',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='imagingobservationorder',
            name='approved_by',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='imagingobservationorder',
            name='approved_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='imagingobservationorder',
            name='bill',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='imagingobservationorder',
            name='patient',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='imagingobservationorder',
            name='report',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='imagingobservationorder',
            name='reported_by',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='imagingobservationorder',
            name='reported_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='imagingorder',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
    ]
