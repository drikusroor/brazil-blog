# Generated by Django 5.1.1 on 2024-10-06 19:40

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0003_itinerary_itinerarystop'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itinerarystop',
            name='description',
            field=wagtail.fields.RichTextField(blank=True),
        ),
    ]