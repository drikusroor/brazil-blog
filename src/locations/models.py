# locations/models.py

from django import forms
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import ClusterableModel
from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.snippets.models import register_snippet
from locations.forms import MapPickerWidget


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


class Itinerary(ClusterableModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        InlinePanel("stops", label="Stops", min_num=1),
    ]

    def __str__(self):
        return self.name


class ItineraryStop(ClusterableModel):
    itinerary = ParentalKey(
        "locations.Itinerary", on_delete=models.CASCADE, related_name="stops"
    )
    start_date = models.DateField()
    end_date = models.DateField()

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)

    panels = [
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("location", widget=MapPickerWidget),
    ]

    def __str__(self):
        return f"{self.location.name} ({self.start_date} - {self.end_date})"


register_snippet(Itinerary)
