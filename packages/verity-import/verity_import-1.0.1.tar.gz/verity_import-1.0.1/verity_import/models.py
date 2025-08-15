from netbox.models import NetBoxModel
from django.db import models
from django.urls import reverse


class VeritySource(NetBoxModel):
    verity_url = models.CharField(max_length=200, verbose_name=("URL"))

    class Meta:
        ordering = ('verity_url',)
        verbose_name = "Controller"
        verbose_name_plural = "Controllers"

    def __str__(self):
        return f"Controller: {self.pk}"

    def get_absolute_url(self):
        return reverse('plugins:verity_import:veritysource', args=[self.pk])


class VeritySourceLogin(NetBoxModel):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=50)
    verity_source = models.ForeignKey(
        to=VeritySource,
        on_delete=models.CASCADE,
        related_name='+'
    )

    class Meta:
        ordering = ('verity_source', 'username')
        unique_together = ('verity_source', 'username')
        verbose_name = "Credential"
        verbose_name_plural = "Credentials"

    def __str__(self):
        return f"Credentials: {self.pk}"

    def get_absolute_url(self):
        return reverse('plugins:verity_import:veritysourcelogin', args=[self.pk])


class VerityLastSyncTime(NetBoxModel):
    timestamp = models.DateTimeField()
    verity_source = models.ForeignKey(
        to=VeritySource,
        on_delete=models.CASCADE,
        related_name='+'
    )

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statuses"
        default_permissions = ('view')

    def __str__(self):
        return f"Status: {self.pk}"

    def get_absolute_url(self):
        return reverse('plugins:verity_import:veritysource', args=[self.verity_source.pk])
