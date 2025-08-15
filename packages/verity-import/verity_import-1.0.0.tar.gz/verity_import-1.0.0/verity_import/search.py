from netbox.search import SearchIndex, register_search
from .models import VeritySource, VeritySourceLogin


@register_search
class VeritySourceIndex(SearchIndex):
    model = VeritySource
    fields = (
        ('verity_url', 100),
        ('pk', 5000),
    )


@register_search
class VeritySourceLoginIndex(SearchIndex):
    model = VeritySourceLogin
    fields = (
        ('username', 100),
        ('password', 5000),
    )
