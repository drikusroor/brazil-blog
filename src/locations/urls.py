from django.urls import path
from . import views

urlpatterns = [
    path(
        "itinerary/",
        views.itinerary_overview,
        name="itinerary_overview",
    ),
]
