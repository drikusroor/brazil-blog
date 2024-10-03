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


# make an itinerary form that does some checks:
# - a stop's start_date must be before end_date
# - a stop's start_date must be after the previous stop's end_date
class ItineraryForm(WagtailAdminModelForm):
    def clean(self):
        cleaned_data = super().clean()

        stops_formset = self.formsets.get("stops")
        if stops_formset and stops_formset.is_valid():
            stops = sorted(
                [
                    form.cleaned_data
                    for form in stops_formset.forms
                    if form.cleaned_data and not form.cleaned_data.get("DELETE", False)
                ],
                key=lambda x: x["start_date"],
            )

            for i, stop in enumerate(stops):
                name = stop.get("name")
                start_date = stop.get("start_date")
                end_date = stop.get("end_date")

                if start_date and end_date:
                    if start_date > end_date:
                        self.add_error(
                            None,
                            f"Stop {i + 1} ({name}) must start before it ends (start_date: {start_date}, end_date: {end_date})",
                        )

                if i > 0:
                    previous_stop = stops[i - 1]
                    previous_name = previous_stop.get("name")
                    previous_end_date = previous_stop.get("end_date")

                    if previous_end_date and start_date:
                        if start_date < previous_end_date:
                            self.add_error(
                                None,
                                f"Stop {i + 1} ({name}) must start after the previous stop ({previous_name}) ends (previous_end_date: {previous_end_date}, start_date: {start_date})",
                            )

        return cleaned_data


class Itinerary(ClusterableModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        InlinePanel("stops", label="Stops", min_num=1),
    ]

    base_form_class = ItineraryForm

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

    def parsed_location(self):
        return self.location.split(",")

    def latitude(self):
        (latitude,) = self.parsed_location()
        return latitude

    def longitude(self):
        (_, longitude) = self.parsed_location()
        return longitude

    panels = [
        FieldPanel("start_date"),
        FieldPanel("end_date"),
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel(
            "location",
            widget=MapPickerWidget,
            attrs={
                "placeholder": "Click on the map to select a location",
                "model_name": "stops",
            },
        ),
    ]

    def __str__(self):
        return f"{self.location.name} ({self.start_date} - {self.end_date})"


register_snippet(Itinerary)
