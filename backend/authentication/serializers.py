from django.conf import settings
from django.contrib.auth.models import update_last_login
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from backend.authentication.models import OTP
from backend.authentication.token_generator import generate_token


class AuthenticationSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return generate_token(token_length=settings.OTP_LENGTH)

    def validate(self, attrs):
        data = super().validate(attrs)
        return {
            **data,
            'user': self.user,
            'token': self.get_token(self.user)
        }


class CustomTokenObtainPairSerializer(serializers.Serializer):
    username = serializers.CharField()
    token = serializers.CharField(max_length=settings.OTP_LENGTH)

    default_error_messages = {
        'no_active_account': _('No active account found with the given credentials')
    }

    def validate(self, attrs):
        otp = OTP.objects.filter(
            user__username=attrs['username'],
            created_at__gte=timezone.now() - timezone.timedelta(seconds=settings.OTP_EXPIRES_AFTER)
        ).latest('created_at')
        user = otp.user

        if not otp or otp.token != attrs['token'] or not api_settings.USER_AUTHENTICATION_RULE(user):
            raise exceptions.AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )
        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)

        return data
