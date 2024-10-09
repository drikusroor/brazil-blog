# games/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import DrinkViewSet

router = DefaultRouter()
router.register(r"drinks", DrinkViewSet, basename="drinks")


urlpatterns = [
    path("api/", include(router.urls)),
]
