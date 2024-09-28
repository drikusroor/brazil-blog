# Generated by Django 5.1.1 on 2024-09-26 14:30

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0013_remove_blogpage_location"),
        ("locations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="location",
            name="page",
            field=modelcluster.fields.ParentalKey(
                default=7,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="location",
                to="blog.blogpage",
            ),
            preserve_default=False,
        ),
    ]