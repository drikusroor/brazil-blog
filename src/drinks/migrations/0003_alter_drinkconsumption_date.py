# Generated by Django 5.1.2 on 2024-10-09 08:48

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drinks', '0002_alter_drinkconsumption_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drinkconsumption',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]