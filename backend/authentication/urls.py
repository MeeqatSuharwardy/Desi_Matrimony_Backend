from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from backend.authentication.views import OTPEmailAPIView, CustomTokenObtainPairView

APP_BASE_URL = 'authentication'

urlpatterns = [
    path(
        APP_BASE_URL + '/authenticate/',
        OTPEmailAPIView.as_view(),
        name='otp_email',
    ),
    path(
        APP_BASE_URL + '/token/generate',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        APP_BASE_URL + '/token/refresh',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
]
