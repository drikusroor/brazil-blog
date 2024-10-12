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
        queryset = self.get_unread_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        logger.debug(f"get_queryset called for user: {self.request.user}")
        return Notification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    def get_unread_queryset(self):
        logger.debug(f"get_unread_queryset called for user: {self.request.user}")
        return self.get_queryset().filter(read=False)

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        logger.debug(f"mark_as_read called for notification {pk}")
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({"status": "notification marked as read"})

    # mark all as read for the current user
    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        logger.debug("mark_all_as_read called")
        Notification.objects.filter(user=request.user).update(read=True)
        return Response({"status": "all notifications marked as read"})
