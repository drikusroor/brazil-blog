# games/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("frogger/", views.frogger, name="frogger"),
]
