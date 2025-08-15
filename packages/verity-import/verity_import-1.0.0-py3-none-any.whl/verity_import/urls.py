from django.urls import path
from . import models, views
from netbox.views.generic import ObjectChangeLogView


urlpatterns = (

    # VeritySource
    path('verity-sources/', views.VeritySourceListView.as_view(), name='veritysource_list'),
    path('verity-sources/add/', views.VeritySourceEditView.as_view(), name='veritysource_add'),
    path('verity-sources/<int:pk>/', views.VeritySourceView.as_view(), name='veritysource'),
    path('verity-sources/<int:pk>/edit/', views.VeritySourceEditView.as_view(), name='veritysource_edit'),
    path('verity-sources/<int:pk>/delete/', views.VeritySourceDeleteView.as_view(), name='veritysource_delete'),
    path('verity-sources/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='veritysource_changelog', kwargs={
        'model': models.VeritySource
    }),

    # VeritySourceLogin
    path('verity-source-logins/', views.VeritySourceLoginListView.as_view(), name='veritysourcelogin_list'),
    path('verity-source-logins/add/', views.VeritySourceLoginEditView.as_view(), name='veritysourcelogin_add'),
    path('verity-source-logins/<int:pk>/', views.VeritySourceLoginView.as_view(), name='veritysourcelogin'),
    path('verity-source-logins/<int:pk>/edit/', views.VeritySourceLoginEditView.as_view(), name='veritysourcelogin_edit'),
    path('verity-source-logins/<int:pk>/delete/', views.VeritySourceLoginDeleteView.as_view(), name='veritysourcelogin_delete'),
    path('verity-source-logins/<int:pk>/changelog/', ObjectChangeLogView.as_view(), name='veritysourcelogin_changelog', kwargs={
        'model': models.VeritySourceLogin
    }),

    # VerityLastSyncTime
    path('verity-last-sync-times/', views.VerityLastSyncTimeListView.as_view(), name='veritylastsynctime_list'),

    # VeritySync
    path('verity-sync/', views.VeritySyncView.as_view(), name='veritysourcelogin_sync'),
)
