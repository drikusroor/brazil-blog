from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, BrazilTimeViewSet

router = DefaultRouter()
router.register(r'comments', CommentViewSet)
router.register(r'brazil_time', BrazilTimeViewSet, basename='brazil-time')


urlpatterns = [
    path('api/', include(router.urls)),
]
