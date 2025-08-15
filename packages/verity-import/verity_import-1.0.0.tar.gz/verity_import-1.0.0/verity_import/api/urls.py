from netbox.api.routers import NetBoxRouter
from . import views


app_name = 'verity_import'

router = NetBoxRouter()
router.register('verity-sources', views.VeritySourceViewSet)
router.register('verity-source-logins', views.VeritySourceLoginViewSet)
router.register('verity-last-sync-times', views.VerityLastSyncTimeViewSet)

urlpatterns = router.urls
