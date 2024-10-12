# games/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import AnimalViewSet, AnimalStatisticsView

router = DefaultRouter()
router.register(r"animals", AnimalViewSet, basename="animals")


urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "animal-statistics/", AnimalStatisticsView.as_view(), name="animal_statistics"
    ),
]
