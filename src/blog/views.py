from django.http import HttpResponse
from django.template import Template, Context
from rest_framework import viewsets
from .models import Comment, BlogPage
from .serializers import CommentSerializer, LikeSerializer, CommentLikeSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

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

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be authenticated to create a comment.")

        serializer.save(author=self.request.user)


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

    @action(detail=True, methods=["post"])
    def toggle_like(self, request, pk=None):
        comment = self.get_object()
        liked = comment.like_toggle(request.user)
        return Response(
            {"liked": liked, "like_count": comment.like_count},
            status=status.HTTP_200_OK,
        )
