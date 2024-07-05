from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from backend.notifications.models import Notification
from backend.notifications.serializers import NotificationSerializer


class NotificationAPIViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet
):
    permission_classes = (IsAuthenticated,)
    queryset = Notification.objects
    serializer_class = NotificationSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user).select_related('content_type')
        return queryset.order_by('-created_at')
