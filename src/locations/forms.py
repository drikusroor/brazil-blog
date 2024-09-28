from django.forms.widgets import TextInput


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
