import logging
from django.http import HttpResponse, JsonResponse
from django.template import Template, Context
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.management import call_command

from rest_framework import viewsets
from .models import Comment, BlogPage, Subscription, User
from .serializers import CommentSerializer, LikeSerializer, CommentLikeSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from notifications.models import Notification

logger = logging.getLogger(__name__)


# Create your views here.
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Optionally restricts the returned comments to a given blog post,
        by filtering against a `post` query parameter in the URL.
        """
        queryset = super().get_queryset()
        post_id = self.request.query_params.get("post")
        if post_id is not None:
            queryset = queryset.filter(post_id=post_id)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("You must be authenticated to create a comment.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = self.perform_create(serializer)
        comment_id = comment.id

        # send notification to post author
        post = serializer.instance.post

        notification_url = f"{post.get_url()}#comment-{comment_id}"

        # parent_id
        parent_comment = request.data.get("parent_comment")

        user_to_notify = (
            post.author
            if not parent_comment
            else Comment.objects.get(id=parent_comment).author
        )

        comment_excerpt = (
            comment.body[:20] + "..." if len(comment.body) > 20 else comment.body
        )

        title = (
            f"New comment on your post: {post.title}"
            if not parent_comment
            else f"New reply to your comment: {comment_excerpt}"
        )
        message = (
            f"{request.user} commented on your post: {post.title}"
            if not parent_comment
            else f"{request.user} replied to your comment: {comment_excerpt}"
        )

        Notification.objects.create(
            user=user_to_notify,
            title=title,
            message=message,
            url=notification_url,
        )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


# public endpoints


@permission_classes([AllowAny])
class BrazilTimeViewSet(viewsets.ViewSet):
    def list(self, request):
        template = Template("{% load brazil_time %}{% display_brazil_time %}")
        context = Context({})
        return HttpResponse(template.render(context))

    def retrieve(self, request, pk=None):
        raise NotImplementedError("GET method is not supported.")

    def create(self, request):
        raise NotImplementedError("POST method is not supported.")

    def update(self, request, pk=None):
        raise NotImplementedError("PUT method is not supported.")

    def partial_update(self, request, pk=None):
        raise NotImplementedError("PATCH method is not supported")

    def destroy(self, request, pk=None):
        raise NotImplementedError("DELETE method is not supported.")


class LikeViewSet(viewsets.ModelViewSet):
    queryset = BlogPage.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def toggle_like(self, request, pk=None):
        post = self.get_object()
        liked = post.like_toggle(request.user)
        return Response(
            {"liked": liked, "like_count": post.like_count}, status=status.HTTP_200_OK
        )


class CommentLikeViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentLikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned comments to a given blog post,
        by filtering against a `post` query parameter in the URL.
        """
        queryset = super().get_queryset()
        comment_id = self.request.query_params.get("comment")
        if comment_id is not None:
            queryset = queryset.filter(comment_id=comment_id)
        return queryset

    @action(detail=True, methods=["post"])
    def toggle_like(self, request, pk=None):
        comment = self.get_object()
        liked = comment.like_toggle(request.user)
        return Response(
            {"liked": liked, "like_count": comment.like_count},
            status=status.HTTP_200_OK,
        )


def posts_by_date(request):
    date_str = request.GET.get("date")
    date = parse_date(date_str)

    if not date:
        return JsonResponse({"error": "Invalid date"}, status=400)

    posts = BlogPage.objects.live().filter(date__date=date).order_by("date")

    post_data = [
        {"title": post.title, "intro": post.intro, "url": post.get_url()}
        for post in posts
    ]

    return JsonResponse({"posts": post_data})


@require_POST
@login_required
def toggle_subscription(request, author_id):
    author = get_object_or_404(User, id=author_id)
    subscriber = request.user

    subscription, created = Subscription.objects.get_or_create(
        subscriber=subscriber, author=author
    )

    if not created:
        subscription.delete()
        subscribed = False
    else:
        subscribed = True

    return JsonResponse({"subscribed": subscribed})


@permission_classes([IsAdminUser])
def send_test_email(request, subscription_id):
    subscription = Subscription.objects.get(id=subscription_id)
    result = subscription.send_test_email(request, subscription_id)
    return JsonResponse({"message": result})


@permission_classes([IsAdminUser])
def send_daily_digest_email(self):
    # call command to send daily digest email
    try:
        call_command("senddailydigest")
        return "Daily digest email sent successfully"
    except Exception as e:
        logger.error(f"Error sending daily digest email: {e}")
        return f"Error: {e}"
