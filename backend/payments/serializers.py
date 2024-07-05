from rest_framework import serializers

from backend.payments.models import PaymentPlan


class PaymentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentPlan
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }


class CreatePaymentIntentRequestSerializer(serializers.Serializer):
    payment_plan = serializers.IntegerField(required=True)


class CreatePaymentIntentResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    object = serializers.CharField()
    client_secret = serializers.CharField()
    public_key = serializers.CharField()
    amount = serializers.IntegerField()
    currency = serializers.CharField()


class PaymentIntentErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()
