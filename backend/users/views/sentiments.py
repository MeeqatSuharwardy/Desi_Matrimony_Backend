from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from backend.users.models import Sentiment
from backend.users.serializers import SentimentSerializer


class SentimentAPIViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Sentiment.objects
    serializer_class = SentimentSerializer

    def get_queryset(self):
        sentiment = self.request.query_params.get('sentiment')
        if sentiment and self.action == 'list':
            return self.queryset.filter(sentiment=sentiment)
        return self.queryset.all()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='sentiment', location=OpenApiParameter.QUERY,
                description='User Sentiment', required=False, type=str, enum=Sentiment.SentimentStatus.values
            )
        ],
    )
    def list(self, request, *args, **kwargs):
        return super(SentimentAPIViewSet, self).list(request, *args, **kwargs)
