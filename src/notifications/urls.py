from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

router = DefaultRouter()
router.register(r"notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="notifications/all-notifications.html"),
        name="all_notifications",
    ),
    path("api/", include(router.urls)),
]
