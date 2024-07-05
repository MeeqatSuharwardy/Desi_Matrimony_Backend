import face_recognition
import numpy as np
from PIL import Image
from django.contrib.auth.hashers import make_password
from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from backend.users.models import User, Sentiment, ProfileView

basic_user_fields = [
    'id', 'username', 'email', 'avatar',
    'first_name', 'last_name', 'password',
    'gender', 'religion', 'blood_group'
]

basic_user_extra_kwargs = {
    'password': {'write_only': True},
    'id': {'read_only': True},
    'avatar': {'read_only': True},
}


class UserProfileSentimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_likes', 'profile_dislikes']

    profile_likes = serializers.SerializerMethodField()
    profile_dislikes = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.INT)
    def get_profile_likes(self, obj):
        return obj.sentiments_to.filter(sentiment=Sentiment.SentimentStatus.LIKE).count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_profile_dislikes(self, obj):
        return obj.sentiments_to.filter(sentiment=Sentiment.SentimentStatus.DISLIKE).count()


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = basic_user_fields
        extra_kwargs = basic_user_extra_kwargs

    def validate_avatar(self, value):
        image = Image.open(value.file)
        image = np.array(image.convert('RGB'))
        face_locations = face_recognition.face_locations(image)

        if len(face_locations) > 1:
            raise serializers.ValidationError('More than 1 face detected in the uploaded image')

        if len(face_locations) < 1:
            raise serializers.ValidationError('No face detected in the uploaded image')

        value.file.seek(0)

        return value

    @transaction.atomic
    def create(self, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(
                validated_data['password'])
        return super(UserBasicSerializer, self).create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(
                validated_data['password'])

        if 'avatar' in validated_data and not validated_data['avatar']:
            del validated_data['avatar']

        return super(UserBasicSerializer, self).update(instance, validated_data)


class UserDetailSerializer(UserProfileSentimentSerializer, UserBasicSerializer):
    class Meta:
        model = User
        exclude = [
            'user_permissions', 'groups',
            'created_at', 'updated_at', 'date_joined',
            'is_staff', 'is_superuser', 'last_login',
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'id': {'read_only': True},
            'is_active': {'write_only': True, 'required': False}
        }

    profile_viewers = serializers.SerializerMethodField()
    profile_views = serializers.SerializerMethodField()
    payment_plan_title = serializers.ReadOnlyField()
    is_payment_plan_expired = serializers.ReadOnlyField()

    @extend_schema_field(OpenApiTypes.INT)
    def get_profile_viewers(self, obj):
        # TODO: obj.viewee.all().distinct('viewer').count()
        # TODO: after migrating to PostgreSQL
        return User.objects.filter(viewer__viewee=obj).distinct().count()

    @extend_schema_field(OpenApiTypes.INT)
    def get_profile_views(self, obj):
        return obj.viewee.all().count()


class UserBasicSentimentSerializer(UserProfileSentimentSerializer, UserBasicSerializer):
    class Meta:
        model = User
        fields = basic_user_fields + ['sentiment', 'profile_likes', 'profile_dislikes']
        extra_kwargs = basic_user_extra_kwargs

    sentiment = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.STR)
    def get_sentiment(self, obj):
        return getattr(obj, 'sentiment', None)


class UserBasicProfileViewSerializer(UserProfileSentimentSerializer, UserBasicSerializer):
    class Meta:
        model = User
        fields = basic_user_fields + ['view_count', 'last_viewed', 'profile_likes', 'profile_dislikes']
        extra_kwargs = basic_user_extra_kwargs

    view_count = serializers.SerializerMethodField()
    last_viewed = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.INT)
    def get_view_count(self, obj):
        return getattr(obj, 'view_count', None)

    @extend_schema_field(OpenApiTypes.STR)
    def get_last_viewed(self, obj):
        return getattr(obj, 'last_viewed', None)


class SentimentSerializer(serializers.ModelSerializer):
    class Meta:
        validators = []
        model = Sentiment
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    @transaction.atomic
    def create(self, validated_data):
        instance, __ = Sentiment.objects.get_or_create(
            sentiment_to=validated_data['sentiment_to'], sentiment_from=validated_data['sentiment_from'])

        instance.sentiment = validated_data['sentiment']
        instance.save()
        return instance


class ProfileViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileView
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
        }
