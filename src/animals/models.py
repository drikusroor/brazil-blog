from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from wagtail.models import ClusterableModel
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from locations.forms import MapPickerWidget

User = get_user_model()


class AnimalType(ClusterableModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional image for the animal type",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("image"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class AnimalSpotting(ClusterableModel):
    spotter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="animal_spottings",
    )

    description = models.TextField(blank=True)

    animal_type = models.ForeignKey(
        AnimalType, on_delete=models.CASCADE, related_name="animal_spottings"
    )
    # default count is 1
    count = models.PositiveIntegerField(default=1)
    # default is the current date
    date = models.DateTimeField(default=timezone.now)
    # location of spotting
    location = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel("spotter"),
        FieldPanel("description"),
        FieldPanel("animal_type"),
        FieldPanel("count"),
        FieldPanel("date"),
        FieldPanel("location", widget=MapPickerWidget),
    ]

    def __str__(self):
        return f"{self.animal_type} - {self.date}"


register_snippet(AnimalType)
register_snippet(AnimalSpotting)
