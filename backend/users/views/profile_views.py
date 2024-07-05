from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from backend.users.models import ProfileView
from backend.users.serializers import ProfileViewSerializer
from services.date_service import DateService


class ProfileViewAPIViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = ProfileView.objects
    serializer_class = ProfileViewSerializer

    def get_queryset(self):
        queryset = self.queryset
        start_date = self.request.query_params.get('start')
        end_date = self.request.query_params.get('end')

        if not (start_date or end_date or self.action != 'list'):
            return queryset.all()

        if start_date:
            start_date = DateService.from_timestamp(start_date)
            queryset = queryset.filter(created_at__gte=start_date)

        if end_date:
            end_date = DateService.from_timestamp(end_date)
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset

    @extend_schema(
        parameters=[
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
    def list(self, request, *args, **kwargs):
        return super(ProfileViewAPIViewSet, self).list(request, *args, **kwargs)
