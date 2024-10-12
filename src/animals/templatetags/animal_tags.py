from django import template
from django.utils.safestring import mark_safe
from django.db.models import Sum
from ..models import AnimalType, AnimalSpotting
from django.urls import reverse

register = template.Library()


@register.simple_tag
def quick_animal_add_buttons():
    animal_types = AnimalType.objects.all()
    buttons_html = '<div class="grid grid-cols-2 gap-4">'
    for animal_type in animal_types:
        image_url = (
            animal_type.image.get_rendition("fill-50x50").url
            if animal_type.image
            else ""
        )
        buttons_html += f"""
            <button class="animal-add-btn relative p-0 border-none bg-transparent cursor-pointer focus:outline-none group" data-animal-type="{animal_type.id}" title="Add {animal_type.name}">
                <img src="{image_url}" alt="{animal_type.name}" width="50" height="50" class="rounded-full">
                <span class="absolute -right-1 -bottom-1 bg-green-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold group-hover:bg-green-600 transition-colors">+</span>
            </button>
        """
    buttons_html += "</div>"
    return mark_safe(buttons_html)


@register.simple_tag
def show_total_animals_spotted():
    total = AnimalSpotting.objects.aggregate(total=Sum("count"))["total"]

    statistics_url = reverse("animal_statistics")

    html = f"""
        <a class="text-center text-xs flex items-center bg-green-700 text-white p-1 gap-1 rounded" href="{statistics_url}" title="Total animals spotted: 🦛 {total}">
            <img src="/static/images/capybara.png" alt="Animal" class="w-4 h-4">
            <span class="">{total}</span>
        </a>
    """

    return mark_safe(html)
