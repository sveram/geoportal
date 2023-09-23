from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import path, include

from gisweb.commonview import Commonviews
from gisweb.views import Home, Panel
from gisweb import commonview as m


def logoutpru(request):
    logout(request)
    return HttpResponseRedirect('/')


urlpatterns = [
    path(r'',Panel.as_view(),name='gis_web_home'),
    path(r'logout',logoutpru,name='logout'),
    path(r'reset/password/', m.ResetPasswordView.as_view(), name='reset_password'),
    path(r'change/password/<str:token>/', m.ChangePasswordView.as_view(), name='change_password'),
    path(r'login',Commonviews.as_view(), name='loginper')
]
