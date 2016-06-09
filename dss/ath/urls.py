from django.conf.urls import patterns, include, url
from . import views
urlpatterns = [
                   url(r'^login$',views.login),
                   url(r'^auth_view$',views.auth_view),
                   url(r'^loggedin$',views.loggedin),
                   url(r'^invalid_login$',views.invalid_login),
                   url(r'^logout$',views.logout),
                   url(r'^signup$',views.signup),
                   url(r'^register_success$',views.register_success),
                   url(r'^require_login$',views.require_login),
                   url(r'^permission_error$',views.permission_error),
                   url(r'^profile$',views.profile)
                ]