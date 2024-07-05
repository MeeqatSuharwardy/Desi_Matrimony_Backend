from django.db import models
from django.db.models import Q
from django.utils import timezone

from backend.events.enum import EventStatus


class EventQuerySet(models.QuerySet):
    def filter_by_event_status(self, status, **kwargs):
        query = Q(**kwargs)

        if status and status.lower() == EventStatus.PAST.value:
            query = query & Q(end_date__lt=timezone.now())
        elif status and status.lower() == EventStatus.PENDING.value:
            query = query & Q(end_date__gte=timezone.now())

        return self.filter(query)

    def filter_past_events(self, **kwargs):
        return self.filter_by_event_status(EventStatus.PAST.value, **kwargs)

    def filter_pending_events(self, **kwargs):
        return self.filter_by_event_status(EventStatus.PENDING.value, **kwargs)
