# Generated by Django 5.1.6 on 2025-02-24 20:23

import django.contrib.auth.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicleLending', '0003_user_password'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(default='defaultpassword', max_length=255),
        ),
    ]
