from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import path

from gisweb.views.base.category_view import CategoryListView, CategoryCreateUpdateView, CategoryDeleteView
from gisweb.views.base.default_data import get_categories, get_records, get_indicators_v2, \
    get_subcategories_v2, get_records_by_indicators
from gisweb.views.base.indicator_view import IndicatorListView, IndicatorCreateUpdateView, IndicatorDeleteView
from gisweb.views.base.source_type_view import SourceTypeListView, SourceTypeCreateUpdateView, SourceTypeDeleteView
from gisweb.views.base.subcategory_view import SubCategoryListView, SubCategoryCreateUpdateView, SubCategoryDeleteView
from gisweb.views.commonview import CommonViews
from gisweb.views.export_to_shp import export_shapefile
from gisweb.views.indicator_view import IndicatorRecordListView, IndicatorRecordCreateUpdateView, \
    IndicatorRecordDeleteView, IndicatorRecordCreateFromTemplateView
from gisweb.views.sector_type_views import SectorTypeListView, SectorTypeDeleteView, SectorTypeCreateUpdateView
from gisweb.views.sector_views import SectorListView, SectorCreateUpdateView, get_parent_sectors, save_location, \
    get_gis_record, get_sectors
from gisweb.views import commonview as m
from gisweb.views.template_views import IndicatorTemplateListView, IndicatorTemplateDeleteView, \
    IndicatorTemplateCreateUpdateView, get_subcategories, get_indicators
from gisweb.views.views import Panel, CargarSectoresView, CargarMapSectoreView


def logoutpru(request):
    logout(request)
    return HttpResponseRedirect('/')


urlpatterns = [
    path(r'', Panel.as_view(), name='gis_web_home'),

    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('category/create-update/', CategoryCreateUpdateView.as_view(), name='category-create-update'),
    path('category/delete/<int:pk>/', CategoryDeleteView.as_view(), name='category-delete'),

    path('subcategories/', SubCategoryListView.as_view(), name='subcategory-list'),
    path('subcategory/create-update/', SubCategoryCreateUpdateView.as_view(), name='subcategory-create-update'),
    path('subcategory/delete/<int:pk>/', SubCategoryDeleteView.as_view(), name='subcategory-delete'),

    path('indicators/', IndicatorListView.as_view(), name='indicator-list'),
    path('indicator/create-update/', IndicatorCreateUpdateView.as_view(), name='indicator-create-update'),
    path('indicator/delete/<int:pk>/', IndicatorDeleteView.as_view(), name='indicator-delete'),

    path('source-types/', SourceTypeListView.as_view(), name='source-type-list'),
    path('source-type/create-update/', SourceTypeCreateUpdateView.as_view(), name='source-type-create-update'),
    path('source-type/delete/<int:pk>/', SourceTypeDeleteView.as_view(), name='source-type-delete'),

    path('ajax/cargar-sectores/', CargarSectoresView.as_view(), name='cargar_sectores'),
    path('ajax/cargar-geom-sector/', CargarMapSectoreView.as_view(), name='cargar_sectores_map'),
    path(r'logout', logoutpru, name='logoutper'),
    path(r'reset/password/', m.ResetPasswordView.as_view(), name='reset_password'),
    path(r'change/password/<str:token>/', m.ChangePasswordView.as_view(), name='change_password'),
    path(r'accounts/login/', CommonViews.as_view(), name='loginper'),

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
    path('ajax/sectors/', get_sectors, name='get_sectors'),

    path('indicator-templates/', IndicatorTemplateListView.as_view(), name='indicator-template-list'),
    path('indicator-template/create/', IndicatorTemplateCreateUpdateView.as_view(), name='indicator-template-create'),
    path('indicator-template/<int:pk>/update/', IndicatorTemplateCreateUpdateView.as_view(),
         name='indicator-template-update'),
    path('indicator-template/<int:pk>/delete/', IndicatorTemplateDeleteView.as_view(),
         name='indicator-template-delete'),
    path('ajax/get-subcategories/', get_subcategories, name='get_subcategories'),
    path('ajax/get-indicators/', get_indicators, name='get_indicators'),
    # path('export/geojson/<int:indicator_template_id>/', export_geojson, name='export_geojson'),
    path('export/shapefile/<int:indicator_template_id>/', export_shapefile, name='export_shapefile'),

    path('records/', IndicatorRecordListView.as_view(), name='indicator-record-list'),
    path('records/create-update/<int:pk>/', IndicatorRecordCreateUpdateView.as_view(), name='indicator-record-update'),
    path('records/create-update/', IndicatorRecordCreateUpdateView.as_view(), name='indicator-record-create'),
    path('records/create-from-template/<int:template_id>/', IndicatorRecordCreateFromTemplateView.as_view(),
         name='create_from_template'),
    path('records/delete/<int:pk>/', IndicatorRecordDeleteView.as_view(), name='indicator-record-delete'),

    path('ajax/get-categories/', get_categories, name='get_categories'),
    path('ajax/subcategories/<int:category_id>/', get_subcategories_v2, name='get_subcategories_v2'),
    path('ajax/indicators/<int:subcategory_id>/', get_indicators_v2, name='get_indicators_v2'),
    path('ajax/get-records/<int:indicator_id>/', get_records, name='get_records'),
    path('ajax/records/', get_records_by_indicators, name='get_records_by_indicator'),

]
