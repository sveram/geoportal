from django.contrib.gis import admin

from .forms import SectorForm
from .models import *

from leaflet.admin import LeafletGeoAdmin


class GISDetailInline(admin.TabularInline):
    model = GISDetailRecord
    extra = 10  # Número de detalles adicionales que se pueden agregar


class GISRecordInline(admin.StackedInline):
    model = GISRecord
    extra = 1  # Permite agregar un nuevo GISRecord en el formulario de Sector
    fk_name = 'associated_gis_record'  # Relación con Sector
    fields = ['gis_type', 'data_file', 'srid', 'point_geometry', 'linestring_geometry', 'polygon_geometry',
              'multipoint_geometry', 'multilinestring_geometry', 'multipolygon_geometry']

    # Para evitar duplicar los GISRecords en el inline, puedes deshabilitar la capacidad de elegir entre varios.
    max_num = 1


class TemplateGISInline(admin.TabularInline):
    model = ExtraDataTemplate
    extra = 1


class GISModelAdmin(LeafletGeoAdmin):
    inlines = [GISDetailInline]


class IndicatorTemplateAdmin(LeafletGeoAdmin):
    inlines = [TemplateGISInline]


admin.site.register(SectorType, LeafletGeoAdmin)


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    form = SectorForm  # Usar el formulario personalizado

    list_display = ('name', 'sector_type', 'parent_sector', 'associated_gis_record')
    search_fields = ('name',)
    list_filter = ('sector_type',)

    def save_model(self, request, obj, form, change):
        # Sobrescribir save_model para usar el formulario personalizado
        form.save()  # Llamar al método save del formulario personalizado

admin.site.register(Person, LeafletGeoAdmin)
admin.site.register(Category, LeafletGeoAdmin)
admin.site.register(SubCategory, LeafletGeoAdmin)
admin.site.register(Indicator, LeafletGeoAdmin)
admin.site.register(SourceType, LeafletGeoAdmin)
admin.site.register(IndicatorTemplate, IndicatorTemplateAdmin)
admin.site.register(GISRecord, GISModelAdmin)
admin.site.register(GISDetailRecord, LeafletGeoAdmin)
admin.site.register(GISTemplate, LeafletGeoAdmin)
