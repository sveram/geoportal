#!/usr/bin/env python

import os
import sys

from geoportal.settings import MEDIA_ROOT

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
your_djangoproject_home = os.path.split(SITE_ROOT)[0]
sys.path.append(your_djangoproject_home)

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "geoportal.settings")
application = get_wsgi_application()

import geopandas as gpd
from gisweb.models import SectorType, Sector, GISRecord, GIS_TYPE_CHOICES, GISDetailRecord
from shapely.geometry.multipolygon import MultiPolygon
from django.contrib.gis.geos import GEOSGeometry


dir_base = os.path.join(MEDIA_ROOT, 'data')
pais = Sector.objects.get(id=462)

type_gis_map = {v: k for k, v in GIS_TYPE_CHOICES}

def add_detail_gis(gis_id,name,detail):
    try:
        detalle = GISDetailRecord(
            gis_record_id=gis_id,
            title=name,
            description=detail
        )
        detalle.save()
        return True, detalle.id
    except Exception as e:
        print(f"Error: {e}({sys.exc_info()[-1].tb_lineno})")
        return False, None

def add_gis_secto(geom, srid=3857):
    try:
        type_gis = 6
        if geom.geom_type == 'Polygon':
            geom = [geom]
            type_gis = 3
        geom = MultiPolygon(geom)
        geom_convert = GEOSGeometry(geom.wkt)
        srid = srid
        gisModel = GISRecord(
            gis_type = type_gis,
            multipolygon_geometry = geom_convert,
            srid=int(srid)
        )
        gisModel.save()
        return True, gisModel.pk
    except Exception as e:
        print(f"Error: {e}({sys.exc_info()[-1].tb_lineno})")
        return False, None
def read_migrate_sectores_prov():
    try:
        shapefile = gpd.read_file(dir_base + "/Provincias1.shp")
        typeSector=SectorType.objects.filter(name__icontains='PROVINCIA').first()
        for index, shp in shapefile.iterrows():
            name = shp.DPA_DESPRO
            geom = shp.geometry
            result, gis_id = add_gis_secto(geom)
            if not result:
                raise NameError(f"No se pudo agregar la provincia {name}")
            if shp.DPA_PROVIN: add_detail_gis(gis_id,'DPA_PROVIN', shp.DPA_PROVIN)
            if shp.OBJECTID: add_detail_gis(gis_id,'OBJECTID', shp.OBJECTID)
            if shp.DPA_ANIO: add_detail_gis(gis_id,'DPA_ANIO', shp.DPA_ANIO)
            if shp.REI_CODIGO: add_detail_gis(gis_id,'REI_CODIGO', shp.REI_CODIGO)
            if shp.DPA_VALOR: add_detail_gis(gis_id,'DPA_VALOR', shp.DPA_VALOR)
            if shp.PEE_CODIGO: add_detail_gis(gis_id,'PEE_CODIGO', shp.PEE_CODIGO)
            if shp.SHAPE_Leng: add_detail_gis(gis_id,'SHAPE_Leng', shp.SHAPE_Leng)
            if shp.SHAPE_Area: add_detail_gis(gis_id,'SHAPE_Area', shp.SHAPE_Area)
            if not Sector.objects.values('id').filter(name=name).exists():
                sector = Sector(
                    sector_type = typeSector,parent_sector=pais,
                    name = name,
                    associated_gis_record_id = gis_id
                )
                sector.save()
                print(f"Sector {name}({typeSector.name})")
    except Exception as ex:
        print(f"Error: {ex}({sys.exc_info()[-1].tb_lineno})")
# read_migrate_sectores_prov()
def read_migrate_sectores_cant():
    try:
        shapefile = gpd.read_file(dir_base + "/Cantones1.shp")
        typeSector = SectorType.objects.filter(name__icontains='CIUDAD').first()
        for index, shp in shapefile.iterrows():
            name = shp.DPA_DESCAN
            geom = shp.geometry
            result, gis_id = add_gis_secto(geom)
            if not result:
                raise NameError(f"No se pudo agregar la provincia {name}")
            mastersector = None
            if shp.DPA_CANTON: add_detail_gis(gis_id, 'DPA_CANTON', shp.DPA_CANTON)
            if shp.DPA_PROVIN: add_detail_gis(gis_id, 'DPA_PROVIN', shp.DPA_PROVIN)
            if shp.DPA_DESPRO:
                add_detail_gis(gis_id, 'DPA_DESPRO', shp.DPA_DESPRO)
                mastersector = Sector.objects.filter(name__icontains=str(shp.DPA_DESPRO)).order_by('-id').first()
            if shp.OBJECTID: add_detail_gis(gis_id, 'OBJECTID', shp.OBJECTID)
            if shp.DPA_ANIO: add_detail_gis(gis_id, 'DPA_ANIO', shp.DPA_ANIO)
            if shp.DPA_VALOR: add_detail_gis(gis_id, 'DPA_VALOR', shp.DPA_VALOR)
            if shp.SHAPE_Leng: add_detail_gis(gis_id, 'SHAPE_Leng', shp.SHAPE_Leng)
            if shp.SHAPE_Area: add_detail_gis(gis_id, 'SHAPE_Area', shp.SHAPE_Area)
            if not Sector.objects.values('id').filter(name=name).exists():
                sector = Sector(
                    sector_type = typeSector,
                    name = name,
                    associated_gis_record_id = gis_id,
                    parent_sector=mastersector
                )
                sector.save()
                print(f"Sector {name}({typeSector.name})")
    except Exception as ex:
        print(f"Error: {ex}({sys.exc_info()[-1].tb_lineno})")
# read_migrate_sectores_cant()
def read_migrate_sectores_parroquias():
    try:
        shapefile = gpd.read_file(dir_base + "/parroquias/Parroquias.shp")
        srid = None
        if not shapefile.crs:
            shapefile.set_crs(epsg=3857, inplace=True)
            srid = 3857
        else :
            crs_info = shapefile.crs

            # Imprimir la información del CRS
            print("Sistema de Referencia Espacial (CRS):", crs_info)

            # Obtener el EPSG/SRID si está disponible
            if crs_info and 'epsg' in crs_info.srs.lower():
                srid = crs_info.srs.split(':')[-1]
        typeSector = SectorType.objects.filter(name__icontains='PARRQUIA').first()
        for index, shp in shapefile.iterrows():
            name = shp.NOMBRE
            geom = shp.geometry
            result, gis_id = add_gis_secto(geom,srid)
            if not result:
                raise NameError(f"No se pudo agregar la provincia {name}")
            mastersector = None
            if shp.PROVINCIA: add_detail_gis(gis_id, 'PROVINCIA', shp.PROVINCIA)
            if shp.CANTON:
                add_detail_gis(gis_id, 'CANTON', shp.CANTON)
                mastersector = Sector.objects.filter(name__icontains=str(shp.CANTON)).order_by('-id').first()
            if shp.CODCANTON: add_detail_gis(gis_id, 'CODCANTON', shp.CODCANTON)
            if shp.CODPRO: add_detail_gis(gis_id, 'CODPRO', shp.CODPRO)
            if shp.AREA: add_detail_gis(gis_id, 'AREA', shp.AREA)
            if shp.PERIMETER: add_detail_gis(gis_id, 'PERIMETER', shp.PERIMETER)
            if not Sector.objects.values('id').filter(name=name).exists():
                sector = Sector(
                    sector_type = typeSector,
                    name = name,
                    associated_gis_record_id = gis_id,
                    parent_sector=mastersector
                )
                sector.save()
                print(f"Sector {name}({typeSector.name})")
    except Exception as ex:
        print(f"Error: {ex}({sys.exc_info()[-1].tb_lineno})")

read_migrate_sectores_parroquias()