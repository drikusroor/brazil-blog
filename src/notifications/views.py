from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
import logging

logger = logging.getLogger(__name__)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer

    def list(self, request):
        logger.debug("NotificationViewSet.list() called")
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        logger.debug(f"get_queryset called for user: {self.request.user}")
        return Notification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        logger.debug(f"mark_as_read called for notification {pk}")
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({"status": "notification marked as read"})
