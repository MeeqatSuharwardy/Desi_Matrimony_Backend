from django.urls import path
from rest_framework.routers import DefaultRouter

from backend.payments.views import StripeTestPaymentAPIView, PaymentPlanAPIViewSet, StripeCreatePaymentIntentAPIView, \
    StripeConfirmPaymentIntentAPIView, StripePaymentEventCallbackAPIView

APP_BASE_URL = 'payments'

urlpatterns = [
    path(
        APP_BASE_URL + '/test-payment/',
        StripeTestPaymentAPIView.as_view(),
        name='test_payment',
    ),
    path(
        APP_BASE_URL + '/create-payment-intent/',
        StripeCreatePaymentIntentAPIView.as_view(),
        name='create_payment_intent',
    ),
    path(
        APP_BASE_URL + '/confirm-payment-intent/',
        StripeConfirmPaymentIntentAPIView.as_view(),
        name='confirm_payment_intent',
    ),
    path(
        APP_BASE_URL + '/payment-events-callback/',
        StripePaymentEventCallbackAPIView.as_view(),
        name='payment_events_callback',
    )
]

router = DefaultRouter()
router.register(APP_BASE_URL + r'/payment-plans', PaymentPlanAPIViewSet, basename='payment_plan')

urlpatterns += router.urls
