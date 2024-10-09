# games/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("frogger/", views.frogger, name="frogger"),
    path("submit-score/", views.submit_score, name="submit_score"),
    path("high-score/", views.top_scores, name="top_scores"),
]
