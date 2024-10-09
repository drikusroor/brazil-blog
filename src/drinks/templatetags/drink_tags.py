from django import template
from django.utils.safestring import mark_safe
from django.db.models import Sum
from ..models import DrinkType, DrinkConsumption
from django.urls import reverse

register = template.Library()


@register.simple_tag
def quick_drink_add_buttons():
    drink_types = DrinkType.objects.all()
    buttons_html = '<div class="grid grid-cols-2 gap-4">'
    for drink_type in drink_types:
        image_url = (
            drink_type.image.get_rendition("fill-50x50").url if drink_type.image else ""
        )
        buttons_html += f"""
            <button class="drink-add-btn relative p-0 border-none bg-transparent cursor-pointer focus:outline-none group" data-drink-type="{drink_type.id}" title="Add {drink_type.name}">
                <img src="{image_url}" alt="{drink_type.name}" width="50" height="50" class="rounded-full">
                <span class="absolute -right-1 -bottom-1 bg-green-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold group-hover:bg-green-600 transition-colors">+</span>
            </button>
        """
    buttons_html += "</div>"
    return mark_safe(buttons_html)


@register.simple_tag
def show_total_drinks_consumed():
    total = DrinkConsumption.objects.aggregate(total=Sum("amount"))["total"]

    statistics_url = reverse("drink_statistics")

    html = f"""
        <a class="text-center text-xs flex items-center bg-green-700 text-white p-1 gap-1 rounded" href="{statistics_url}" title="Total drinks consumed: 🍹 {total}">
            🍹
            <span class="">{total}</span>
        </a>
    """

    return mark_safe(html)
