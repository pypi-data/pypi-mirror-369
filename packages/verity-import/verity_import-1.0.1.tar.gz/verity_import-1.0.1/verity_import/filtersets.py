from netbox.filtersets import NetBoxModelFilterSet
from .models import VeritySourceLogin


class VeritySourceLoginFilterSet(NetBoxModelFilterSet):

    class Meta:
        model = VeritySourceLogin
        fields = ('id', 'verity_source', 'username', 'password')

    def search(self, queryset, name, value):
        return queryset.filter(description__icontains=value)
