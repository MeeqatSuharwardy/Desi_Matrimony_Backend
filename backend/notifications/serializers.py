from generic_relations.relations import GenericRelatedField
from rest_framework import serializers

from backend.notifications.models import Notification
from backend.users.models import ProfileView, Sentiment
from backend.users.serializers import ProfileViewSerializer, SentimentSerializer


class NotificationSerializer(serializers.ModelSerializer):
    content_type = serializers.CharField(source='content_type.model')
    content_object = GenericRelatedField({
        ProfileView: ProfileViewSerializer(),
        Sentiment: SentimentSerializer()
    })

    class Meta:
        model = Notification
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True}
        }
