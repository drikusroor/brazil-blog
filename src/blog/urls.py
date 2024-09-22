from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommentViewSet,
    BrazilTimeViewSet,
    LikeViewSet,
    CommentLikeViewSet,
)

router = DefaultRouter()
router.register(r"comments", CommentViewSet)
router.register(r"brazil_time", BrazilTimeViewSet, basename="brazil-time")
router.register(r"likes", LikeViewSet)
router.register(r"comment-likes", CommentLikeViewSet, basename="comment-likes")


urlpatterns = [
    path("api/", include(router.urls)),
]
