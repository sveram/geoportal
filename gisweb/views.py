import sys

from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import GEOSGeometry
from django.core.serializers import serialize
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator

# Create your views here.
from django.views.generic import TemplateView

from gisweb.commonview import add_data_user
from gisweb.forms import GISRecordForm, IndicatorTemplateForm
# from gisweb.forms import FormCampos
from gisweb.models import Person, Sector, Category, SectorType
from django.http import JsonResponse
from django.views import View
from .models import Sector

@method_decorator(login_required(), name="dispatch")
class CargarSectoresView(View):
    def get(self, request, *args, **kwargs):
        parent_id = request.GET.get('parent_id')  # Obtener el ID del sector padre desde la solicitud
        sectors = Sector.objects.filter(parent_sector_id=parent_id).order_by('name')
        return JsonResponse(list(sectors.values('id', 'name')), safe=False)


@method_decorator(login_required, name='dispatch')
class CargarMapSectoreView(View):
    def get(self, request, *args, **kwargs):
        # Obtener el ID del sector padre desde la solicitud
        parent_id = request.GET.get('sector_id')

        # Obtener los sectores hijos
        sectors = Sector.objects.filter(id=parent_id).select_related('associated_gis_record').order_by(
            'name')

        # Construir la respuesta con la información del sector y la geometría asociada
        sector_data = []

        for sector in sectors:
            gis_record = sector.associated_gis_record
            geom_data = None
            geom_type = None

            if gis_record:
                # Determinar el tipo de geometría y extraer las coordenadas
                if gis_record.gis_type == 1 and gis_record.point_geometry:
                    geom_data = list(gis_record.point_geometry.coords)
                    geom_type = 'Point'
                elif gis_record.gis_type == 2 and gis_record.linestring_geometry:
                    geom_data = list(gis_record.linestring_geometry.coords)
                    geom_type = 'LineString'
                elif gis_record.gis_type == 3 and gis_record.polygon_geometry:
                    geom_data = list(gis_record.polygon_geometry.coords)
                    geom_type = 'Polygon'
                elif gis_record.gis_type == 4 and gis_record.multipoint_geometry:
                    geom_data = [list(point.coords) for point in gis_record.multipoint_geometry]
                    geom_type = 'MultiPoint'
                elif gis_record.gis_type == 5 and gis_record.multilinestring_geometry:
                    geom_data = [list(line.coords) for line in gis_record.multilinestring_geometry]
                    geom_type = 'MultiLineString'
                elif gis_record.gis_type == 6 or gis_record.gis_type == 3 and gis_record.multipolygon_geometry:
                    geom_data = [list(polygon.coords) for polygon in gis_record.multipolygon_geometry]
                    geom_type = 'MultiPolygon'

            # Agregar la información del sector y la geometría a la lista
            sector_data.append({
                'id': sector.id,
                'name': sector.name,
                'geometry_type': geom_type,  # Tipo de geometría (Point, Polygon, etc.)
                'coordinates': geom_data  # Coordenadas de la geometría
            })

        # Devolver los datos en formato JSON
        return JsonResponse(sector_data, safe=False)

@method_decorator(login_required(), name="dispatch")
class Panel(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            form = ''#FormCampos()
            context = {
                'title': 'Home',
                # 'form': form
            }
           # adddatauser(request,context)
            if 'vwa' in request.GET:
                context['vwa'] = vwa = request.GET['vwa']
                if vwa == 'add':
                    try:
                        context['title'] = 'Geographical Location'
                        sector_types = SectorType.objects.all()
                        first_sector_type = sector_types.first()
                        sectors_by_type = Sector.objects.filter(sector_type=first_sector_type,
                                                                                    parent_sector__isnull=True)

                        context['sector_types'] = sector_types
                        context['first_sector_type'] = first_sector_type
                        context['sectors_by_type'] = sectors_by_type
                        form = GISRecordForm()
                        indicator_form = IndicatorTemplateForm()
                        context['pais'] = list(Sector.objects.values_list('id','name').filter(is_active=True, parent_sector__isnull=True))
                        return render(request, 'adm_template/form_template_individual.html', context)
                    except Exception as ex:
                        pass
                elif vwa == 'viewsectores':
                    try:
                        categoria = Category.objects.filter(status=True)
                        context['categoria'] = categoria
                        context['title'] = 'Sectores'
                        return  render(request, 'home/viewsectores.html', context)
                    except Exception as ex:
                        pass
                elif vwa == 'get_coordinates':
                    try:
                        id = request.GET.get('id',None)
                        sect = Sector.objects.get(status=True,id=id)
                        geo_polygon_wkt = sect.geo_polygon.geojson
                        return JsonResponse({'geojsoncoor':geo_polygon_wkt}, safe=False)
                    except Exception as ex:
                        pass
                return HttpResponseRedirect('/')
            else:
                return render(request,'home/home.html',context)
        except Exception as ex:
            print(ex)
            print(sys.exc_info()[-1].tb_lineno)