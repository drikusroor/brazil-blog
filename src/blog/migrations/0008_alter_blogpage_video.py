# Generated by Django 5.0.4 on 2024-08-01 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_blogpage_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpage',
            name='video',
            field=models.URLField(blank=True, null=True),
        ),
    ]
