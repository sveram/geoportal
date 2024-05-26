import sys

from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import GEOSGeometry
from django.core.serializers import serialize
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator

# Create your views here.
from django.views.generic import TemplateView

from gisweb.commonview import adddatauser
from gisweb.forms import FormCampos
from gisweb.models import Person, Sector, Category


class Home(TemplateView):

    template_name = 'home/home.html'

    def get_context_data(self, **kwargs):
        form = FormCampos()
        context = {
            'title':'Inicio',
            'form':form
        }
        self.extra_context = context
        return super().get_context_data()

@method_decorator(login_required(), name="dispatch")
class Panel(TemplateView):

    def get(self, request, *args, **kwargs):
        try:
            form = FormCampos()
            context = {
                'title': 'Inicio',
                # 'form': form
            }
           # adddatauser(request,context)
            if 'vwa' in request.GET:
                context['vwa'] = vwa = request.GET['vwa']
                if vwa == 'add':
                    try:
                        form = FormCampos()
                        context['form'] = form
                        context['title'] = 'Agregar categoría'
                        return render(request,'home/formadd.html',context)
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

#https://github.com/samuel205/open_layer/tree/7086912fa49368d1f7af5899e43c8e92a8f2c16e/data
