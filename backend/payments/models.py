from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class PaymentPlan(models.Model):
    title = models.CharField(_('title'), max_length=128)
    amount = models.IntegerField(_('amount to be charged'), default=1000, help_text=_('1000 means 10$'))
    duration = models.IntegerField(_('duration in days'), default=30)
    currency = models.CharField(_('amount currency'), max_length=3, default='usd')
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return f'{self.title[:16]}...' if len(self.title) > 16 else self.title


class PaymentEvent(models.Model):
    class PaymentEventType(models.TextChoices):
        PAYMENT_INTENT_CREATED = 'payment_intent.created', _('PAYMENT_INTENT_CREATED')
        CHARGE_SUCCEEDED = 'charge.succeeded', _('CHARGE_SUCCEEDED')
        PAYMENT_INTENT_SUCCEEDED = 'payment_intent.succeeded', _('PAYMENT_INTENT_SUCCEEDED')
        PAYMENT_INTENT_PROCESSING = 'payment_intent.processing', _('PAYMENT_INTENT_PROCESSING')
        PAYMENT_INTENT_FAILED = 'payment_intent.payment_failed', _('PAYMENT_INTENT_FAILED')
        UNHANDLED_EVENT = 'unhandled_event', _('UNHANDLED_EVENT')

    payment_intent = models.CharField(max_length=256)
    type = models.CharField(
        _('payment event type'),
        max_length=32,
        choices=PaymentEventType.choices,
        default=PaymentEventType.UNHANDLED_EVENT,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='payment_events'
    )
    payment_plan = models.ForeignKey(
        PaymentPlan,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='payment_events'
    )
    amount = models.IntegerField(_('amount to be charged'), null=True, blank=True)
    currency = models.CharField(_('amount currency'), max_length=3, null=True, blank=True)
    response = models.JSONField(_('payment event response'), default=dict)
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
