from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from leaflet.forms.widgets import LeafletWidget
from django.forms import inlineformset_factory

from .models import *
from crum import get_current_user


class ResetPasswordForm(forms.Form):
    cedula = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Ingrese su cedula',
        'class': 'form-control',
        'autocomplete': 'off'
    }))

    def clean(self):
        cleaned = super().clean()
        if not Person.objects.filter(identificador=cleaned['cedula']).exists():
            self._errors['error'] = self._errors.get('error', self.error_class())
            self._errors['error'].append('No existe usuario registrado con esa cedula')
            # raise forms.ValidationError('No existe usuario registrado con esa cedula')
        return cleaned

    def get_user(self):
        cedula = self.cleaned_data.get('cedula')
        return Person.objects.get(identificador=cedula)


class ChangePasswordForm(forms.Form):
    clave = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Ingrese la contraseña nueva',
        'class': 'form-control',
        'autocomplete': 'off'
    }), label='Contraseña Nueva')

    claveconf = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Repita la contraseña',
        'class': 'form-control',
        'autocomplete': 'off'
    }), label='Repetir contraseña')

    def clean(self):
        cleaned = super().clean()
        clave = cleaned['clave']
        claveconf = cleaned['claveconf']
        if clave != claveconf:
            raise forms.ValidationError('Las contraseñas deben coincidir')
        return cleaned


# class SectorForm(forms.ModelForm):
#     # Campos de GISRecord que se incluirán en el formulario de Sector
#     gis_type = forms.ChoiceField(choices=GIS_TYPE_CHOICES, label='Tipo de Geografía')
#     data_file = forms.FileField(required=False, label='Archivo de Datos (Opcional)')
#     srid = forms.IntegerField(initial=3857, label='SRID')
#
#     class Meta:
#         model = Sector
#         fields = ['sector_type', 'name', 'parent_sector']
#
#     def save(self, commit=True):
#         # Guardamos primero el Sector
#         sector = super().save(commit=False)
#
#         # Crear o asociar un GISRecord
#         gisrecord = GISRecord(
#             gis_type=self.cleaned_data['gis_type'],
#             data_file=self.cleaned_data.get('data_file'),
#             srid=self.cleaned_data['srid']
#         )
#         if commit:
#             gisrecord.save()  # Guardar el GISRecord
#             sector.associated_gis_record = gisrecord  # Asociar el GISRecord al Sector
#             sector.save()  # Guardar el Sector con el GISRecord asociado
#
#         return sector

class IndicatorRecordForm(forms.ModelForm):
    class Meta:
        model = IndicatorRecord
        fields = ['indicator','sector','source_type', 'gis', 'name', 'value', 'date']


class GISRecordForm(forms.ModelForm):
    class Meta:
        model = GISRecord
        fields = ['gis_type', 'point_geometry', 'linestring_geometry', 'polygon_geometry',
                  'multipoint_geometry', 'multilinestring_geometry', 'multipolygon_geometry']


class IndicatorTemplateForm(forms.ModelForm):
    class Meta:
        model = IndicatorTemplate
        fields = ['person', 'indicator', 'description']


class ExtraDataTemplateForm(forms.ModelForm):
    class Meta:
        model = ExtraDataTemplate
        fields = ['value_type', 'name', 'precision']


class GISTemplateForm(forms.ModelForm):
    class Meta:
        model = GISTemplate
        fields = ['sector']


# Crear formset para manejar los datos extra relacionados con el indicador
ExtraDataFormSet = inlineformset_factory(
    IndicatorTemplate, ExtraDataTemplate, form=ExtraDataTemplateForm,
    extra=1, can_delete=True
)


class LocationForm(forms.Form):
    pais = forms.ModelChoiceField(
        queryset=Sector.objects.filter(parent_sector__isnull=True),  # Nivel 0, solo países
        label="País",
        required=True
    )
    provincia = forms.ModelChoiceField(
        queryset=Sector.objects.none(),  # Se llena dinámicamente
        label="Provincia",
        required=False
    )
    canton = forms.ModelChoiceField(
        queryset=Sector.objects.none(),  # Se llena dinámicamente
        label="Cantón",
        required=False
    )
    parroquia = forms.ModelChoiceField(
        queryset=Sector.objects.none(),  # Se llena dinámicamente
        label="Parroquia",
        required=False
    )

    class Meta:
        fields = ['pais', 'provincia', 'canton', 'parroquia']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'pais' in self.data:
            try:
                pais_id = int(self.data.get('pais'))
                self.fields['provincia'].queryset = Sector.objects.filter(parent_sector_id=pais_id)
            except (ValueError, TypeError):
                pass
        if 'provincia' in self.data:
            try:
                provincia_id = int(self.data.get('provincia'))
                self.fields['canton'].queryset = Sector.objects.filter(parent_sector_id=provincia_id)
            except (ValueError, TypeError):
                pass
        if 'canton' in self.data:
            try:
                canton_id = int(self.data.get('canton'))
                self.fields['parroquia'].queryset = Sector.objects.filter(parent_sector_id=canton_id)
            except (ValueError, TypeError):
                pass


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'name']


class IndicatorForm(forms.ModelForm):
    class Meta:
        model = Indicator
        fields = ['subcategory', 'name']


class SectorTypeForm(forms.ModelForm):
    class Meta:
        model = SectorType
        fields = ['order', 'name']
        labels = {
            'order': 'Order',
            'name': 'Sector Type Name'
        }
        widgets = {
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ['sector_type', 'name', 'parent_sector', ]
        widgets = {
            'sector_type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_sector': forms.Select(attrs={'class': 'form-control select2'}),
            # 'associated_gis_record': forms.Select(attrs={'class': 'form-control'}),
        }
