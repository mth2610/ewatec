from django.conf.urls import patterns, include, url
from . import views
urlpatterns = [
               url(r'^upload$',views.upload),
               url(r'^upload_methods$',views.upload_methods),
               url(r'^upload_sources$',views.upload_sources),
               url(r'^upload_variables$',views.upload_variables),
               url(r'^upload_sites$',views.upload_sites),
               url(r'^upload_datavalues$',views.upload_datavalues),
               url(r'^confirm_upload$',views.confirm_upload),
               url(r'^save_methods$',views.save_methods),
               url(r'^save_sources$',views.save_sources),
               url(r'^save_variables$',views.save_variables),
               url(r'^save_sites$',views.save_sites),
               url(r'^save_datavalues$',views.save_datavalues),
               url(r'^delete_sites$',views.delete_sites),
               url(r'^delete_data$',views.deleteData),
               url(r'^updateEditedData$',views.updateEditedData),
               url(r'^download_sample/(?P<name>.+)/$',views.download_sample),
             ]