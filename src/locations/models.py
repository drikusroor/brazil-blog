# locations/models.py

from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel


class Location(models.Model):
    page = ParentalKey(
        "blog.BlogPage", on_delete=models.CASCADE, related_name="location"
    )

    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.TextField(blank=True)

    content_panels = [
        FieldPanel("name"),
        FieldPanel("latitude"),
        FieldPanel("longitude"),
        FieldPanel("description"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
