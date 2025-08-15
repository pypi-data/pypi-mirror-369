from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from ..models import VeritySource, VeritySourceLogin, VerityLastSyncTime
from ipam.api.serializers import PrefixSerializer


class NestedVeritySourceSerializer(WritableNestedSerializer):

    class Meta:
        model = VeritySource
        fields = ('id', 'url', 'display', 'verity_url')

class NestedVeritySourceLoginSerializer(WritableNestedSerializer):

    class Meta:
        model = VeritySourceLogin
        fields = ('id', 'url', 'display', 'username')

class NestedVerityLastSyncTimeSerializer(WritableNestedSerializer):

    class Meta:
        model = VerityLastSyncTime
        fields = ('id', 'url', 'display', 'timestamp')


class VeritySourceSerializer(NetBoxModelSerializer):

    class Meta:
        model = VeritySource
        fields = (
            'id', 'display', 'url', 'verity_url', 'tags', 'custom_fields', 'created',
            'last_updated',
        )


class VeritySourceLoginSerializer(NetBoxModelSerializer):

    verity_source = NestedVeritySourceSerializer()

    class Meta:
        model = VeritySourceLogin
        fields = (
            'id', 'url', 'display', 'verity_source', 'username', 'password', 'tags', 'custom_fields', 'created',
            'last_updated',
        )


class VerityLastSyncTimeSerializer(NetBoxModelSerializer):

    verity_source = NestedVeritySourceSerializer()

    class Meta:
        model = VerityLastSyncTime
        fields = (
            'id', 'url', 'display', 'verity_source', 'timestamp', 'tags', 'custom_fields', 'created',
            'last_updated',
        )
