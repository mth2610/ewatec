from django.conf.urls import patterns, include, url
from . import views
urlpatterns = [
               url(r'^view_contact$',views.contact),
               ## url(r'^save_contact$',views.save_contact)
               ]
