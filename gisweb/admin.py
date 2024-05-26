from django.contrib.gis import admin
from .models import *

from leaflet.admin import LeafletGeoAdmin

admin.site.register(TypeSector, LeafletGeoAdmin)
admin.site.register(Sector, LeafletGeoAdmin)
admin.site.register(Category, LeafletGeoAdmin)
admin.site.register(SubCategory, LeafletGeoAdmin)
admin.site.register(Indicator, LeafletGeoAdmin)
admin.site.register(TypeSource, LeafletGeoAdmin)
admin.site.register(IndicatorData, LeafletGeoAdmin)

