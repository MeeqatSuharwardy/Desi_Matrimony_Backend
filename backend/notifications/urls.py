from rest_framework.routers import DefaultRouter

from backend.notifications.views import NotificationAPIViewSet

APP_BASE_URL = 'notifications'

router = DefaultRouter()
router.register(APP_BASE_URL, NotificationAPIViewSet, basename='notifications')

urlpatterns = router.urls
