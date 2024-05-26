from django.contrib.gis import admin
from .models import *

from leaflet.admin import LeafletGeoAdmin

class GISDetailInline(admin.TabularInline):
    model = GISDetail
    extra = 10  # Número de detalles adicionales que se pueden agregar

class GISModelAdmin(LeafletGeoAdmin):
    inlines = [GISDetailInline]

admin.site.register(TypeSector, LeafletGeoAdmin)
admin.site.register(Sector, LeafletGeoAdmin)
admin.site.register(Category, LeafletGeoAdmin)
admin.site.register(SubCategory, LeafletGeoAdmin)
admin.site.register(Indicator, LeafletGeoAdmin)
admin.site.register(TypeSource, LeafletGeoAdmin)
admin.site.register(IndicatorData, LeafletGeoAdmin)
admin.site.register(GISModel, GISModelAdmin)
admin.site.register(GISDetail, LeafletGeoAdmin)

