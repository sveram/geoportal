#!/usr/bin/env python

import os
import sys

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
your_djangoproject_home = os.path.split(SITE_ROOT)[0]
sys.path.append(your_djangoproject_home)

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoportal.settings")
application = get_wsgi_application()

import geopandas as gpd
from gisweb.models import TypeSector, Sector
from shapely.geometry.multipolygon import MultiPolygon
from django.contrib.gis.geos import GEOSGeometry

dir_base = '/mnt/c/Users/PERSONAL/Downloads/Provincias/'

def read_migrate_sectores_prov():
    try:
        shapefile = gpd.read_file(dir_base + "Provincias1.shp")
        typeSector = TypeSector.objects.get(id=2)
        for index, shp in shapefile.iterrows():
            name = shp.DPA_DESPRO
            geom = shp.geometry
            if geom.geom_type == 'Polygon':
                geom = [geom]
            geom = MultiPolygon(geom)
            geom_convert = GEOSGeometry(geom.wkt)
            if not Sector.objects.values('id').filter(name=name).exists():
                sector = Sector(
                    type_sector = typeSector,
                    name = name,
                    geo_polygon = geom_convert
                )
                sector.save()
                print(f"Sector {name}({typeSector.name})")
    except Exception as ex:
        print(f"Error: {ex}({sys.exc_info()[-1].tb_lineno})")
#read_migrate_sectores_prov()
def read_migrate_sectores_cant():
    try:
        shapefile = gpd.read_file(dir_base + "Cantones/Cantones1.shp")
        typeSector = TypeSector.objects.get(id=4)
        for index, shp in shapefile.iterrows():
            name = shp.DPA_DESCAN
            geom = shp.geometry
            if geom.geom_type == 'Polygon':
                geom = [geom]
            geom = MultiPolygon(geom)
            geom_convert = GEOSGeometry(geom.wkt)
            if not Sector.objects.values('id').filter(name=name).exists():
                sector = Sector(
                    type_sector = typeSector,
                    name = name,
                    geo_polygon = geom_convert
                )
                sector.save()
                print(f"Sector {name}({typeSector.name})")
    except Exception as ex:
        print(f"Error: {ex}({sys.exc_info()[-1].tb_lineno})")
read_migrate_sectores_cant()

