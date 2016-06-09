from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from home import views as home_views
from database import views as database_views
from rest_api import views as api_views
from rest_framework import routers

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'sites', api_views.SiteViewSet)

urlpatterns = [
   url(r'^api/', include(router.urls)),
   url(r'^api/datavalues', api_views.DataValueView.as_view()),
   url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
   url(r'^$', home_views.index),
   url(r'^admin/', include(admin.site.urls)),
   url(r'^gis/', include('gis_apps.urls')),
   url(r'^auth/', include('ath.urls')),
   url(r'^database/', include('database.urls')),
   url(r'^contact/', include('contact.urls')),
   url(r'^documents/', include('documents.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
