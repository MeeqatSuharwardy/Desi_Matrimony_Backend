from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_otp')
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    token = models.CharField(_('auth token'), max_length=settings.OTP_LENGTH)
