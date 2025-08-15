import django_tables2 as tables
from netbox.tables import NetBoxTable
from django.utils.html import format_html
from .models import VeritySource, VeritySourceLogin, VerityLastSyncTime


class VeritySourceTable(NetBoxTable):

    def render_verity_url(self, record):
        if record.verity_url:
            return format_html('<a href="{}" target="_blank">{}</a>',
                               record.verity_url,
                               record.verity_url)
        return "N/A"

    class Meta(NetBoxTable.Meta):
        model = VeritySource
        fields = ('pk', 'verity_url', 'actions')
        default_columns = ('verity_url')


class VeritySourceLoginTable(NetBoxTable):

    verity_source = tables.Column(verbose_name="Verity URL")

    def render_password(self, value):
        return "********"  # Always return a masked value

    def render_verity_source(self, record):
        if record.verity_source and record.verity_source.verity_url:
            return format_html('<a href="{}" target="_blank">{}</a>',
                               record.verity_source.verity_url,
                               record.verity_source.verity_url)
        return "N/A"

    class Meta(NetBoxTable.Meta):
        model = VeritySourceLogin
        fields = ('pk', 'verity_source', 'username', 'password', 'actions')
        default_columns = ('pk', 'verity_source', 'username', 'password')


class VerityLastSyncTimeTable(NetBoxTable):

    verity_source = tables.Column(verbose_name="Verity URL")

    def render_verity_source(self, record):
        if record.verity_source and record.verity_source.verity_url:
            return format_html('<a href="{}" target="_blank">{}</a>',
                               record.verity_source.verity_url,
                               record.verity_source.verity_url)
        return "N/A"

    class Meta(NetBoxTable.Meta):
        model = VerityLastSyncTime
        fields = ('pk', 'verity_source', 'timestamp')
        default_columns = ('pk', 'verity_source', 'timestamp')
        exclude = ('actions',)
