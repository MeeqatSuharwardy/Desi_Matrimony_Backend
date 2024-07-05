from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from backend.events.models import Event, UserEvent


class EventDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    attend_count = serializers.SerializerMethodField()
    not_attend_count = serializers.SerializerMethodField()
    ignore_count = serializers.SerializerMethodField()
    interest_status = serializers.SerializerMethodField()
    user_event = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.INT)
    def get_attend_count(self, obj):
        return getattr(obj, 'attend_count', None)

    @extend_schema_field(OpenApiTypes.INT)
    def get_not_attend_count(self, obj):
        return getattr(obj, 'not_attend_count', None)

    @extend_schema_field(OpenApiTypes.INT)
    def get_ignore_count(self, obj):
        return getattr(obj, 'ignore_count', None)

    @extend_schema_field(OpenApiTypes.STR)
    def get_interest_status(self, obj):
        return getattr(obj, 'interest_status', None)

    @extend_schema_field(OpenApiTypes.INT)
    def get_user_event(self, obj):
        return getattr(obj, 'user_event', None)


class UserEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEvent
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }
