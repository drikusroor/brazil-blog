from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommentViewSet,
    BrazilTimeViewSet,
    LikeViewSet,
    CommentLikeViewSet,
    posts_by_date,
)

router = DefaultRouter()
router.register(r"comments", CommentViewSet)
router.register(r"brazil_time", BrazilTimeViewSet, basename="brazil-time")
router.register(r"likes", LikeViewSet)
router.register(r"comment-likes", CommentLikeViewSet, basename="comment-likes")


# path('api/posts-by-date/', posts_by_date, name='posts_by_date'),
# router.register(r"posts-by-date", posts_by_date, basename="posts-by-date")

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/posts-by-date/", posts_by_date, name="posts_by_date"),
]
