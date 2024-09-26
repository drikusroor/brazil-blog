from django import forms
from wagtail.snippets.models import register_snippet
from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.admin.ui.tables import UpdatedAtColumn
from wagtail.snippets.views.snippets import SnippetViewSet
from django.forms.widgets import TextInput

from .models import Location


class MapPickerWidget(TextInput):
    template_name = "widgets/map_picker.html"

    class Media:
        css = {"all": ("https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",)}
        js = (
            "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
            "js/map_picker.js",
        )

    def __init__(self, attrs=None):
        default_attrs = {"class": "map-picker-input"}
        if attrs:
            default_attrs.update(attrs)

        super().__init__(default_attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["map_id"] = f"map-{context['widget']['attrs']['id']}"
        return context


class LocationForm(WagtailAdminModelForm):
    location = forms.CharField(
        widget=MapPickerWidget(
            attrs={
                "placeholder": "Click on the map to select a location",
                "latitude_field_name": "latitude",
                "longitude_field_name": "longitude",
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields[
                "location"
            ].initial = f"{self.instance.latitude},{self.instance.longitude}"

    def save(self, commit=True):
        instance = super().save(commit=False)
        location = self.cleaned_data.get("location")
        if location:
            lat, lon = location.split(",")
            instance.latitude = float(lat)
            instance.longitude = float(lon)
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Location
        fields = [
            "name",
            "latitude",
            "longitude",
        ]


class LocationViewSet(SnippetViewSet):
    model = Location
    icon = "user"
    list_display = ["name", "get_latitude_readable", UpdatedAtColumn()]
    list_per_page = 50
    copy_view_enabled = False
    inspect_view_enabled = True
    admin_url_namespace = "location_views"
    base_url_path = "internal/location"

    base_form_class = LocationForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_form_class(self, for_update=False):
        return LocationForm


register_snippet(Location, viewset=LocationViewSet)
