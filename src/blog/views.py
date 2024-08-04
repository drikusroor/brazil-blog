from django.http import HttpResponse
from django.template import Template, Context
from rest_framework import viewsets
from .models import Comment
from .serializers import CommentSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

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
        post_id = self.request.query_params.get('post')
        if post_id is not None:
            queryset = queryset.filter(post_id=post_id)
        return queryset
    
    def perform_create(self, serializer):

        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be authenticated to create a comment.")

        serializer.save(author=self.request.user)

# public endpoints

@permission_classes([AllowAny])
class BrazilTimeViewSet(viewsets.ViewSet):

    def list(self, request):
        template = Template('{% load brazil_time %}{% display_brazil_time %}')
        context = Context({})
        return HttpResponse(
            template.render(context))

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

