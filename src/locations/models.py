# locations/models.py

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Location(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.TextField(blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("latitude"),
        FieldPanel("longitude"),
        FieldPanel("description"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
