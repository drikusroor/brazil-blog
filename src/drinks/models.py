from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from wagtail.models import ClusterableModel
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from locations.forms import MapPickerWidget

User = get_user_model()


class DrinkType(ClusterableModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional image for the drink type",
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


# Create your models here.
class DrinkConsumption(ClusterableModel):
    consumer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="drink_consumptions",
    )

    description = models.TextField(blank=True)

    drink_type = models.ForeignKey(DrinkType, on_delete=models.CASCADE)
    # default amount is 1
    amount = models.PositiveIntegerField(default=1)
    # default is the current date
    date = models.DateTimeField(default=timezone.now)
    # location of consumption
    location = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel("consumer"),
        FieldPanel("description"),
        FieldPanel("drink_type"),
        FieldPanel("amount"),
        FieldPanel("date"),
        FieldPanel("location", widget=MapPickerWidget),
    ]

    def __str__(self):
        return f"{self.drink_type} - {self.date}"


register_snippet(DrinkType)
register_snippet(DrinkConsumption)
