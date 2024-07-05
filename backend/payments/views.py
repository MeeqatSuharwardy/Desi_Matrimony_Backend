from datetime import timedelta

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from backend.payments.models import PaymentPlan, PaymentEvent
from backend.payments.serializers import (
    PaymentPlanSerializer, CreatePaymentIntentRequestSerializer,
    CreatePaymentIntentResponseSerializer, PaymentIntentErrorResponseSerializer
)

stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model()


class PaymentPlanAPIViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = PaymentPlanSerializer

    def get_queryset(self):
        return PaymentPlan.objects.filter(is_active=True).order_by('amount', 'created_at')


class StripeTestPaymentAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        payment_intent = stripe.PaymentIntent.create(
            amount=1000,
            currency='cad',
            payment_method_types=['card'],
            receipt_email='test@example.com'
        )
        data = {
            **payment_intent,
            'public_key': settings.STRIPE_PUBLIC_KEY
        }
        return Response(status=status.HTTP_200_OK, data=data)


class StripeConfirmPaymentIntentAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=inline_serializer(
                    name='ConfirmPaymentIntentResponseSerializer',
                    fields={
                        'message': serializers.CharField(default="Success"),
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=PaymentIntentErrorResponseSerializer)
        },
        request=inline_serializer(
            name='ConfirmPaymentIntentRequestSerializer',
            fields={
                'payment_intent_id': serializers.CharField(required=True),
            }
        )
    )
    def post(self, request):
        data = request.data
        payment_intent_id = data['payment_intent_id']
        try:
            stripe.PaymentIntent.confirm(payment_intent_id)
            return Response(status=status.HTTP_200_OK, data={"message": "Success"})
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': str(e)})


class StripeCreatePaymentIntentAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        responses={
            status.HTTP_200_OK: OpenApiResponse(response=CreatePaymentIntentResponseSerializer),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(response=PaymentIntentErrorResponseSerializer),
            status.HTTP_403_FORBIDDEN: OpenApiResponse(response=PaymentIntentErrorResponseSerializer),
        },
        request=CreatePaymentIntentRequestSerializer
    )
    def post(self, request):
        try:
            payment_plan = PaymentPlan.objects.get(
                is_active=True,
                id=request.data.get('payment_plan')
            )

            payment_intent = stripe.PaymentIntent.create(
                amount=payment_plan.amount,
                currency=payment_plan.currency,
                automatic_payment_methods={
                    'enabled': True,
                },
                metadata={
                    'user': request.user.id,
                    'payment_plan': payment_plan.id
                }
            )

            status_code = status.HTTP_200_OK
            data = {
                **payment_intent,
                'public_key': settings.STRIPE_PUBLIC_KEY
            }

        except PaymentPlan.DoesNotExist:
            status_code = status.HTTP_400_BAD_REQUEST
            data = {'error': 'payment plan is either inactive or does not exists'}

        except Exception as e:
            status_code = status.HTTP_403_FORBIDDEN
            data = {'error': str(e)}

        return Response(status=status_code, data=data)


class StripePaymentEventCallbackAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        payload = request.data

        if payload and payload['object'] != 'event':
            return Response(status=status.HTTP_200_OK)

        response_object = (payload.get('data') or {}).get('object') or {}

        payment_intent = response_object.get('id') or ''
        amount = response_object.get('amount')
        currency = response_object.get('currency')
        metadata = response_object.get('metadata') or {}
        user = User.objects.filter(id=metadata.get('user')).first()
        payment_plan = PaymentPlan.objects.filter(id=metadata.get('payment_plan')).first()
        event_type = payload['type']

        payment_event, __ = PaymentEvent.objects.get_or_create(type=event_type, payment_intent=payment_intent)

        payment_event.user = payment_event.user or user
        payment_event.payment_plan = payment_event.payment_plan or payment_plan
        payment_event.amount = payment_event.amount or amount
        payment_event.currency = payment_event.currency or currency
        payment_event.response = payment_event.response or payload
        payment_event.save()

        if user and event_type == PaymentEvent.PaymentEventType.PAYMENT_INTENT_SUCCEEDED:
            user.payment_plan = payment_plan
            now = timezone.now()
            user.payment_plan_expires_at = now + timedelta(days=payment_plan.duration)
            user.payment_plan_subscribed_at = now
            user.save()

        return Response(status=status.HTTP_200_OK)
