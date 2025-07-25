# Generated by Django 4.0.4 on 2022-09-01 14:44

import api.apps.finance.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_alter_invoice_options_bill_invoice_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='serviced_rendered_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='inv_id',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='scheme_type',
            field=models.CharField(choices=[('SELF', 'SELF'), ('INSURANCE', 'INSURANCE')], default=api.apps.finance.models.PayerSchemeType.SELF_PREPAID, max_length=256),
        ),
        migrations.AlterField(
            model_name='bill',
            name='bill_source',
            field=models.CharField(choices=[('ENCOUNTERS', 'Encounter'), ('IMAGING', 'Imaging'), ('LABORATORY', 'Laboratory')], max_length=256),
        ),
    ]
