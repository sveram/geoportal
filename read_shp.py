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
from gisweb.models import TypeSector, Sector, GISModel, TYPE_GIS, GISDetail
from shapely.geometry.multipolygon import MultiPolygon
from django.contrib.gis.geos import GEOSGeometry

dir_base = '/mnt/c/Users/PERSONAL/Downloads/Provincias/'

type_gis_map = {v: k for k, v in TYPE_GIS}

def add_detail_gis(gis_id,name,detail):
    try:
        detalle = GISDetail(
            gismodel_id=gis_id,
            name=name,
            detail=detail
        )
        detalle.save()
        return True, detalle.id
    except Exception as e:
        print(f"Error: {e}({sys.exc_info()[-1].tb_lineno})")
        return False, None

def add_gis_secto(geom):
    try:
        if geom.geom_type == 'Polygon':
            geom = [geom]
        type_gis = type_gis_map.get(str(geom.geom_type), 0)
        geom = MultiPolygon(geom)
        geom_convert = GEOSGeometry(geom.wkt)
        gisModel = GISModel(
            type_gis = type_gis,
            multipolygon = geom_convert
        )
        gisModel.save()

        return True, gisModel.pk
    except Exception as e:
        print(f"Error: {e}({sys.exc_info()[-1].tb_lineno})")
        return False, None
def read_migrate_sectores_prov():
    try:
        shapefile = gpd.read_file(dir_base + "Provincias1.shp")
        typeSector = TypeSector.objects.get(id=2)
        for index, shp in shapefile.iterrows():
            name = shp.DPA_DESPRO
            geom = shp.geometry
            result, gis_id = add_gis_secto(geom)
            if not result:
                raise NameError(f"No se pudo agregar la provincia {name}")
            add_detail_gis(gis_id,'DPA_PROVIN', shp.DPA_PROVIN)
            add_detail_gis(gis_id,'OBJECTID', shp.OBJECTID)
            add_detail_gis(gis_id,'DPA_ANIO', shp.DPA_ANIO)
            add_detail_gis(gis_id,'REI_CODIGO', shp.REI_CODIGO)
            add_detail_gis(gis_id,'DPA_VALOR', shp.DPA_VALOR)
            add_detail_gis(gis_id,'PEE_CODIGO', shp.PEE_CODIGO)
            add_detail_gis(gis_id,'SHAPE_Leng', shp.SHAPE_Leng)
            add_detail_gis(gis_id,'SHAPE_Area', shp.SHAPE_Area)
            if not Sector.objects.values('id').filter(name=name).exists():
                sector = Sector(
                    type_sector = typeSector,
                    name = name,
                    gismodel_id = gis_id
                )
                sector.save()
                print(f"Sector {name}({typeSector.name})")
    except Exception as ex:
        print(f"Error: {ex}({sys.exc_info()[-1].tb_lineno})")
read_migrate_sectores_prov()
def read_migrate_sectores_cant():
    try:
        shapefile = gpd.read_file(dir_base + "Cantones/Cantones1.shp")
        typeSector = TypeSector.objects.get(id=4)
        for index, shp in shapefile.iterrows():
            name = shp.DPA_DESCAN
            geom = shp.geometry
            result, gis_id = add_gis_secto(geom)
            if not result:
                raise NameError(f"No se pudo agregar la provincia {name}")
            add_detail_gis(gis_id, 'DPA_CANTON', shp.DPA_CANTON)
            add_detail_gis(gis_id, 'DPA_PROVIN', shp.DPA_PROVIN)
            add_detail_gis(gis_id, 'DPA_DESPRO', shp.DPA_DESPRO)
            add_detail_gis(gis_id, 'OBJECTID', shp.OBJECTID)
            add_detail_gis(gis_id, 'DPA_ANIO', shp.DPA_ANIO)
            add_detail_gis(gis_id, 'DPA_VALOR', shp.DPA_VALOR)
            add_detail_gis(gis_id, 'SHAPE_Leng', shp.SHAPE_Leng)
            add_detail_gis(gis_id, 'SHAPE_Area', shp.SHAPE_Area)

            if not Sector.objects.values('id').filter(name=name).exists():
                sector = Sector(
                    type_sector = typeSector,
                    name = name,
                    gismodel_id = gis_id
                )
                sector.save()
                print(f"Sector {name}({typeSector.name})")
    except Exception as ex:
        print(f"Error: {ex}({sys.exc_info()[-1].tb_lineno})")
read_migrate_sectores_cant()