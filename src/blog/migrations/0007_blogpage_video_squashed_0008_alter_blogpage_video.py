# Generated by Django 5.0.6 on 2024-08-05 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('blog', '0007_blogpage_video'), ('blog', '0008_alter_blogpage_video')]

    dependencies = [
        ('blog', '0006_authorindexpage_blogpage_author_authorpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpage',
            name='video',
            field=models.URLField(blank=True, null=True),
        ),
    ]
