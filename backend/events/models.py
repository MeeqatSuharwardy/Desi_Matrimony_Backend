from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from backend.events.managers import EventQuerySet

User = get_user_model()


class Event(models.Model):
    class Meta:
        ordering = ['start_date']

    objects = EventQuerySet.as_manager()

    title = models.CharField(_('title'), max_length=512)
    detail = RichTextField(_('detail'), null=True, blank=True)
    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    address = models.CharField(_('address'), max_length=1024)
    city = models.CharField(_('city'), max_length=256)
    state = models.CharField(_('state'), max_length=256)
    country = models.CharField(_('country'), max_length=256)
    is_active = models.BooleanField(_('is active'), default=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return self.title


class UserEvent(models.Model):
    class Meta:
        unique_together = [['event', 'user']]

    class InterestStatus(models.TextChoices):
        ATTEND = 'A', _('Attend')
        NOT_ATTEND = 'N', _('Not Attend')
        IGNORE = 'I', _('Ignore')

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='user_events')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_events')
    interest_status = models.CharField(
        _('interest status'),
        max_length=1,
        choices=InterestStatus.choices,
        default=InterestStatus.IGNORE,
    )
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return f'{self.event.id} | {self.interest_status} | {self.user}'
