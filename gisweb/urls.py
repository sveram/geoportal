from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import path, include

from gisweb.commonview import CommonViews
from gisweb.sector_type_views import SectorTypeListView, SectorTypeDeleteView, SectorTypeCreateUpdateView
from gisweb.sector_views import SectorListView, SectorCreateUpdateView, get_parent_sectors, save_location, \
    get_gis_record
from gisweb.views import Panel, CargarSectoresView, CargarMapSectoreView
from gisweb import commonview as m


def logoutpru(request):
    logout(request)
    return HttpResponseRedirect('/')


urlpatterns = [
    path(r'', Panel.as_view(), name='gis_web_home'),
    path('ajax/cargar-sectores/', CargarSectoresView.as_view(), name='cargar_sectores'),
    path('ajax/cargar-geom-sector/', CargarMapSectoreView.as_view(), name='cargar_sectores_map'),
    path(r'logout', logoutpru, name='logoutper'),
    path(r'reset/password/', m.ResetPasswordView.as_view(), name='reset_password'),
    path(r'change/password/<str:token>/', m.ChangePasswordView.as_view(), name='change_password'),
    path(r'login', CommonViews.as_view(), name='loginper'),

    path('sector_type/', SectorTypeListView.as_view(), name='sector_type_list'),
    path('sector_type/add/', SectorTypeCreateUpdateView.as_view(), name='sector_type_create'),
    path('sector_type/<int:pk>/edit/', SectorTypeCreateUpdateView.as_view(), name='sector_type_edit'),
    path('sector_type/<int:pk>/delete/', SectorTypeDeleteView.as_view(), name='sector_type_delete'),

    path('sectors', SectorListView.as_view(), name='sector_list'),
    path('sectors/add/', SectorCreateUpdateView.as_view(), name='sector_create'),
    path('sectors/<int:pk>/edit/', SectorCreateUpdateView.as_view(), name='sector_edit'),
    path('sectors/save-location/', save_location, name='save_location'),
    path('sectors/<int:pk>/get-gis/', get_gis_record, name='get_gis_record'),
    path('ajax/get-parent-sectors/', get_parent_sectors, name='get_parent_sectors'),
]
