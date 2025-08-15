from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from .models import VeritySource, VeritySourceLogin, VerityLastSyncTime
from utilities.forms.fields import CommentField, DynamicModelChoiceField


class VeritySourceForm(NetBoxModelForm):

    comments = CommentField()

    class Meta:
        model = VeritySource
        fields = ('verity_url', 'comments', 'tags')


class VeritySourceLoginForm(NetBoxModelForm):

    comments = CommentField()
    verity_source = DynamicModelChoiceField(
        queryset=VeritySource.objects.all()
    )

    class Meta:
        model = VeritySourceLogin
        fields = ('verity_source', 'username', 'password', 'comments', 'tags')


class VeritySourceLoginFilterForm(NetBoxModelFilterSetForm):
    model = VeritySourceLogin

    verity_source = forms.ModelMultipleChoiceField(
        queryset=VeritySource.objects.all(),
        required=False
    )
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=50)


class VerityLastSyncTimeForm(NetBoxModelForm):

    comments = CommentField()
    verity_source = DynamicModelChoiceField(
        queryset=VeritySource.objects.all()
    )

    class Meta:
        model = VerityLastSyncTime
        fields = ('verity_source', 'timestamp', 'comments', 'tags')
