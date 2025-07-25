# Generated by Django 4.0.4 on 2022-11-22 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_stockmovementline_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stockmovement',
            options={'permissions': (('approve_stock_movement', 'Can approve stock movement'), ('cancel_stock_movemnet', 'Can cancel stock movement'), ('move_stock', 'Can perform stock movements')), 'verbose_name_plural': 'StockMovements'},
        ),
        migrations.AddField(
            model_name='stockmovement',
            name='moved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='stockmovement',
            name='moved_by',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='stockmovementline',
            name='moved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='stockmovementline',
            name='moved_by',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='store',
            name='is_pharmacy',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='stockmovement',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Draft'), ('APPROVED', 'Approved'), ('CANCELLED', 'Cancelled'), ('DONE', 'Done')], default='DRAFT', max_length=128),
        ),
        migrations.AlterField(
            model_name='stockmovementline',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Draft'), ('APPROVED', 'Approved'), ('CANCELLED', 'Cancelled'), ('DONE', 'Done')], max_length=128),
        ),
        migrations.AlterField(
            model_name='store',
            name='type',
            field=models.CharField(choices=[('CUSTOMER', 'Customer'), ('VENDOR', 'Vendor'), ('INVENTORY LOSS', 'Inventory Loss'), ('CONSUMPTION', 'Consumption'), ('STORE', 'Store'), ('SUPPLIER', 'Supplier')], max_length=218),
        ),
    ]
