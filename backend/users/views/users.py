from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models import Subquery, OuterRef, Count, Q
from django.http import QueryDict
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, filters
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from backend.events.enum import EventStatus
from backend.events.models import Event, UserEvent
from backend.events.serializers import EventDetailSerializer
from backend.users.models import Sentiment, User, ProfileView
from backend.users.serializers import (
    UserDetailSerializer, UserBasicSerializer, UserBasicSentimentSerializer, UserBasicProfileViewSerializer
)
from backend.users.tokens import account_activation_token
from services.date_service import DateService


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user)

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, User):
            return obj == request.user


event_status_query_parameter = OpenApiParameter(
    name='status', location=OpenApiParameter.QUERY,
    description='Event Status', required=False, type=str, enum=[es.value for es in EventStatus]
)

event_interest_query_parameter = OpenApiParameter(
    name='interest', location=OpenApiParameter.QUERY,
    description='User Interest Status', required=False, type=str, enum=UserEvent.InterestStatus.values
)

extend_user_sentiment_schema = extend_schema(
    responses=UserBasicSentimentSerializer(many=True),
    parameters=[
        OpenApiParameter(
            name='id', location=OpenApiParameter.PATH,
            description='A unique integer value identifying this user.',
            required=True, type=int
        ),
        OpenApiParameter(
            name='sentiment', location=OpenApiParameter.QUERY,
            description='User Sentiment', required=False, type=str, enum=[
                value for value in Sentiment.SentimentStatus.values if value != Sentiment.SentimentStatus.NEUTRAL
            ]
        )
    ],
)

extend_profile_views_schema = extend_schema(
    responses=UserBasicProfileViewSerializer(many=True),
    parameters=[
        OpenApiParameter(
            name='id', location=OpenApiParameter.PATH,
            description='A unique integer value identifying this user.',
            required=True, type=int
        ),
        OpenApiParameter(
            name='start_date', location=OpenApiParameter.QUERY,
            description='start date UTC unix timestamp', required=False, type=str
        ),
        OpenApiParameter(
            name='end_date', location=OpenApiParameter.QUERY,
            description='end date UTC unix timestamp', required=False, type=str
        )
    ],
)

GET_USER_EVENTS_ACTION = 'get_events'


class UserAPIViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserDetailSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('created_at',)
    ordering = '-created_at'

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            elif self.action != GET_USER_EVENTS_ACTION:
                self._paginator = CursorPagination()
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_users_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_serializer_class(self):
        if self.action == GET_USER_EVENTS_ACTION:
            return EventDetailSerializer
        elif self.action == 'list':
            return UserBasicSerializer
        elif self.action in ['get_user_sentiments_from', 'get_user_sentiments_to']:
            return UserBasicSentimentSerializer
        elif self.action in ['get_profile_visited_by', 'get_profile_visited_to']:
            return UserBasicProfileViewSerializer

        return super(UserAPIViewSet, self).get_serializer_class()

    def get_queryset(self):
        if self.action == 'get_user_sentiments_from':
            return self.get_user_sentiments_from_queryset()
        elif self.action == 'get_user_sentiments_to':
            return self.get_user_sentiments_to_queryset()
        elif self.action == GET_USER_EVENTS_ACTION:
            return self.get_user_events_queryset()
        elif self.action == 'get_profile_visited_by':
            return self.get_profile_visited_by_queryset()
        elif self.action == 'get_profile_visited_to':
            return self.get_profile_visited_to_queryset()

        return self.get_users_queryset()

    def get_users_queryset(self):
        return User.objects.all()

    def get_user_sentiments_from_queryset(self):
        sentiment = self.request.query_params.get('sentiment')
        user = self.get_object()

        query = {
            'sentiments_from__sentiment_to': user
        }
        if sentiment:
            query['sentiments_from__sentiment'] = sentiment

        queryset = User.objects.filter(
            **query
        ).annotate(
            sentiment=Subquery(
                Sentiment.objects.filter(
                    sentiment_from=OuterRef('id'),
                    sentiment_to=user
                ).values('sentiment')[:1]
            )
        )
        return queryset.exclude(sentiment=Sentiment.SentimentStatus.NEUTRAL)

    def get_user_sentiments_to_queryset(self):
        sentiment = self.request.query_params.get('sentiment')
        user = self.get_object()

        query = {
            'sentiments_to__sentiment_from': user
        }
        if sentiment:
            query['sentiments_to__sentiment'] = sentiment

        queryset = User.objects.filter(
            **query
        ).annotate(
            sentiment=Subquery(
                Sentiment.objects.filter(
                    sentiment_to=OuterRef('id'),
                    sentiment_from=user
                ).values('sentiment')[:1]
            )
        )
        return queryset.exclude(sentiment=Sentiment.SentimentStatus.NEUTRAL)

    def get_user_events_queryset(self):
        status = self.request.query_params.get('status')
        interest = self.request.query_params.get('interest')

        queryset = Event.objects
        if status and status.lower() == EventStatus.PAST.value:
            queryset = queryset.filter_past_events()
        elif status and status.lower() == EventStatus.PENDING.value:
            queryset = queryset.filter_pending_events()

        query = Q(user_events__user=self.get_object())
        if interest:
            query = query & Q(user_events__interest_status=interest)
        else:
            query = query & ~Q(user_events__interest_status=UserEvent.InterestStatus.IGNORE)

        queryset = queryset.filter(query).annotate(
            attend_count=Count(
                'user_events',
                filter=Q(user_events__interest_status=UserEvent.InterestStatus.ATTEND)
            ),
            not_attend_count=Count(
                'user_events',
                filter=Q(user_events__interest_status=UserEvent.InterestStatus.NOT_ATTEND)
            ),
            ignore_count=Count(
                'user_events',
                filter=Q(user_events__interest_status=UserEvent.InterestStatus.IGNORE)
            ),
            interest_status=Subquery(
                UserEvent.objects.filter(
                    event=OuterRef('id'),
                    user=self.request.user
                ).values('interest_status')[:1]
            ),
            user_event=Subquery(
                UserEvent.objects.filter(
                    event=OuterRef('id'),
                    user=self.request.user
                ).values('id')[:1]
            )
        )

        return queryset.order_by('-end_date')

    def get_profile_visited_by_queryset(self):
        user = self.get_object()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        queryset = User.objects.filter(
            viewer__viewee=user
        )
        sub_queryset = ProfileView.objects.filter(viewee=user)
        view_count_query = Q()

        if start_date:
            start_date = DateService.from_timestamp(start_date)
            queryset = queryset.filter(viewer__created_at__gte=start_date)
            sub_queryset = sub_queryset.filter(created_at__gte=start_date)
            view_count_query = view_count_query & Q(viewee__created_at__gte=start_date)

        if end_date:
            end_date = DateService.from_timestamp(end_date)
            queryset = queryset.filter(viewer__created_at__lte=end_date)
            sub_queryset = sub_queryset.filter(created_at__lte=end_date)
            view_count_query = view_count_query & Q(viewer__created_at__lte=end_date)

        queryset = queryset.annotate(
            view_count=Count(
                'viewer',
                filter=view_count_query
            ),
            last_viewed=Subquery(
                sub_queryset.filter(
                    viewer=OuterRef('id')
                ).order_by('-created_at').values('created_at')[:1]
            )
        ).filter(
            view_count__gt=0
        ).distinct()

        return queryset.order_by('-last_viewed')

    def get_profile_visited_to_queryset(self):
        user = self.get_object()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        queryset = User.objects.filter(
            viewee__viewer=user
        )
        sub_queryset = ProfileView.objects.filter(viewer=user)
        view_count_query = Q()

        if start_date:
            start_date = DateService.from_timestamp(start_date)
            queryset = queryset.filter(viewee__created_at__gte=start_date)
            sub_queryset = sub_queryset.filter(created_at__gte=start_date)
            view_count_query = view_count_query & Q(viewee__created_at__gte=start_date)

        if end_date:
            end_date = DateService.from_timestamp(end_date)
            queryset = queryset.filter(viewee__created_at__lte=end_date)
            sub_queryset = sub_queryset.filter(created_at__lte=end_date)
            view_count_query = view_count_query & Q(viewee__created_at__lte=end_date)

        queryset = queryset.annotate(
            view_count=Count(
                'viewee',
                filter=view_count_query
            ),
            last_viewed=Subquery(
                sub_queryset.filter(
                    viewee=OuterRef('id')
                ).order_by('-created_at').values('created_at')[:1]
            )
        ).filter(
            view_count__gt=0
        ).distinct()

        return queryset.order_by('-last_viewed')

    def is_create_api(self):
        return self.action == 'create'

    def get_permissions(self):
        if self.is_create_api():
            return [AllowAny()]
        return super(UserAPIViewSet, self).get_permissions()

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, QueryDict):  # optional
            request.data._mutable = True

        request.data.update({'is_active': False})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        self.send_activation_email(request, user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def send_activation_email(self, request, user):
        current_site = get_current_site(request)
        mail_subject = 'Matrimony Account Activation Link.'
        message = render_to_string('acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        to_email = user.email
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.send()

    @extend_schema(
        responses=EventDetailSerializer(many=True),
        parameters=[
            OpenApiParameter(
                name='id', location=OpenApiParameter.PATH,
                description='A unique integer value identifying this user.',
                required=True, type=int
            ),
            event_status_query_parameter,
            event_interest_query_parameter
        ],
    )
    @action(detail=True, methods=['get'], url_path='events')
    def get_events(self, request, *args, **kwargs):
        return super(UserAPIViewSet, self).list(request, *args, **kwargs)

    @extend_user_sentiment_schema
    @action(detail=True, methods=['get'], url_path='sentiment-from')
    def get_user_sentiments_from(self, request, *args, **kwargs):
        return super(UserAPIViewSet, self).list(request, *args, **kwargs)

    @extend_user_sentiment_schema
    @action(detail=True, methods=['get'], url_path='sentiment-to')
    def get_user_sentiments_to(self, request, *args, **kwargs):
        return super(UserAPIViewSet, self).list(request, *args, **kwargs)

    @extend_profile_views_schema
    @action(detail=True, methods=['get'], url_path='profile-visited-by')
    def get_profile_visited_by(self, request, *args, **kwargs):
        return super(UserAPIViewSet, self).list(request, *args, **kwargs)

    @extend_profile_views_schema
    @action(detail=True, methods=['get'], url_path='profile-visited-to')
    def get_profile_visited_to(self, request, *args, **kwargs):
        return super(UserAPIViewSet, self).list(request, *args, **kwargs)
