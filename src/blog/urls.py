from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CommentViewSet,
    BrazilTimeViewSet,
    LikeViewSet,
    CommentLikeViewSet,
    posts_by_date,
    toggle_subscription,
    send_test_email,
    send_daily_digest_email,
)

router = DefaultRouter()
router.register(r"comments", CommentViewSet)
router.register(r"brazil_time", BrazilTimeViewSet, basename="brazil-time")
router.register(r"likes", LikeViewSet)
router.register(r"comment-likes", CommentLikeViewSet, basename="comment-likes")

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/posts-by-date/", posts_by_date, name="posts_by_date"),
    path(
        "api/toggle-subscription/<int:author_id>/",
        toggle_subscription,
        name="toggle_subscription",
    ),
    path(
        "api/send-test-email/<int:subscription_id>/",
        send_test_email,
        name="send_test_email",
    ),
    path(
        "api/send-daily-digest-email/",
        send_daily_digest_email,
        name="send_daily_digest_email",
    ),
]
