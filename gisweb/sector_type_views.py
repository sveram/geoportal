from django.db.models import Max
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, View
from .models import SectorType, Sector
from .forms import SectorTypeForm
from django.shortcuts import get_object_or_404


# List view
class SectorTypeListView(ListView):
    model = SectorType
    template_name = 'base_sector_type/sector_type_list.html'
    context_object_name = 'sector_types'

    # Override to filter only active sectors
    def get_queryset(self):
        return SectorType.objects.filter(is_active=True)

        # Override to add extra context

    def get_context_data(self, **kwargs):
        # Llama al método original para obtener el contexto base
        context = super().get_context_data(**kwargs)
        # Agrega el título al contexto
        context['title'] = 'Sector Types'
        return context


# Create and Update views handled via AJAX in the same view
class SectorTypeCreateUpdateView(View):
    def post(self, request, pk=None):
        sector_id = pk
        max_order=0
        if sector_id:
            # Update the existing sector type
            sector_type = get_object_or_404(SectorType, id=sector_id, is_active=True)
            form = SectorTypeForm(request.POST, instance=sector_type)
        else:
            # Create new sector type
            form = SectorTypeForm(request.POST)
            if not form.data.get('order'):
                max_order = SectorType.objects.filter(is_active=True).aggregate(Max('order'))['order__max']
                if max_order is None:
                    max_order = 0  # If no orders exist, start from 0

        if form.is_valid():
            if not pk:
                form.cleaned_data['order'] = max_order + 1
                object_save = SectorType(
                    name=form.cleaned_data['name'],
                    order=form.cleaned_data['order']
                )
                object_save.save()
            else:
                form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})

    def get(self, request, pk):
        sector_type = get_object_or_404(SectorType, pk=pk, is_active=True)
        data = {
            'id': sector_type.id,
            'order': sector_type.order,
            'name': sector_type.name
        }
        return JsonResponse(data)


# Logical delete (set is_active to False)
class SectorTypeDeleteView(View):
    def delete(self, request, pk):
        sector_type = get_object_or_404(SectorType, pk=pk, is_active=True)
        sector_type.is_active = False  # Perform logical delete
        sector_type.save()
        return JsonResponse({'success': True})
