# Generated by Django 5.1.2 on 2024-10-09 11:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drinks', '0003_alter_drinkconsumption_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drinkconsumption',
            name='drink_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drink_consumptions', to='drinks.drinktype'),
        ),
    ]
