# locations/models.py

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface
from wagtail.admin.ui.tables import UpdatedAtColumn
from wagtail.snippets.views.snippets import SnippetViewSet


class Location(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.TextField(blank=True)

    def get_latitude_readable(self):
        # if latitude is higher than 0, it is in the northern hemisphere
        if self.latitude > 0:
            return f"{self.latitude} N"

        # if latitude is lower than 0, it is in the southern hemisphere
        return f"{self.latitude} S"

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
