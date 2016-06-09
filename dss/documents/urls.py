from django.conf.urls import patterns, include, url
from . import views
urlpatterns = [
               url(r'^documents$',views.documents),
               url(r'^newpaper$',views.newpaper),
               url(r'^create$',views.create),
               url(r'^papercontent$',views.papercontent),
               url(r'^(?P<article_id>\d+)/$',views.papercontent),
               url(r'^showpage/(?P<page>\d+)/$',views.showpaper),
               ]
