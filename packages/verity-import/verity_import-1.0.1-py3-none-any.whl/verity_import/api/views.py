from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets, models
from .serializers import VeritySourceLoginSerializer, VeritySourceSerializer, VerityLastSyncTimeSerializer


class VeritySourceViewSet(NetBoxModelViewSet):
    queryset = models.VeritySource.objects.prefetch_related('tags')
    serializer_class = VeritySourceSerializer


class VeritySourceLoginViewSet(NetBoxModelViewSet):
    queryset = models.VeritySourceLogin.objects.prefetch_related(
        'verity_source', 'source_prefix', 'destination_prefix', 'tags'
    )
    serializer_class = VeritySourceLoginSerializer
    filterset_class = filtersets.VeritySourceLoginFilterSet


class VerityLastSyncTimeViewSet(NetBoxModelViewSet):
    queryset = models.VerityLastSyncTime.objects.prefetch_related(
        'verity_source', 'source_prefix', 'destination_prefix', 'tags'
    )
    serializer_class = VerityLastSyncTimeSerializer
