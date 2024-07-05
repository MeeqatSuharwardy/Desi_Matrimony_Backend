from rest_framework.routers import DefaultRouter

from backend.events.views.events import EventsAPIViewSet, UserEventsAPIViewSet

router = DefaultRouter()
router.register(r'events', EventsAPIViewSet, basename='event')
router.register(r'user-events', UserEventsAPIViewSet, basename='user_event')

urlpatterns = router.urls
