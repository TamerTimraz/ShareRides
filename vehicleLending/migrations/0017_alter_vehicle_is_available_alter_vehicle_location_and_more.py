# Generated by Django 5.1.6 on 2025-04-07 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicleLending', '0016_vehicle_requested_alter_vehicle_is_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='is_available',
            field=models.BooleanField(blank=True, default=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='location',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='make',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='model',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='vehicle_type',
            field=models.CharField(choices=[('Bicycle', 'Bicycle'), ('Car', 'Car'), ('Truck', 'Truck'), ('Van', 'Van'), ('Motorcycle', 'Motorcycle')], max_length=255),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='year',
            field=models.CharField(max_length=255),
        ),
    ]
