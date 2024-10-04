from django.shortcuts import render
from .models import Itinerary

# import date
from datetime import date


def itinerary_overview(request):
    # get first itinerary
    itinerary = Itinerary.objects.first()

    # get current date
    current_date = date.today()

    # get the current_stop, aka the stop that is happening today, aka the stop that has the start_date <= current_date <= end_date
    current_stop_id = (
        itinerary.stops.filter(start_date__lte=current_date, end_date__gte=current_date)
        .first()
        .id
    )

    context = {
        "itinerary": itinerary,
        "current_stop_id": current_stop_id,
    }

    return render(request, "itinerary_overview.html", context)
