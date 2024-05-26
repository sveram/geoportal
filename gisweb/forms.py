from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from .models import *
from crum import get_current_user

class ResetPasswordForm(forms.Form):
    cedula = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Ingrese su cedula',
        'class':'form-control',
        'autocomplete':'off'
    }))

    def clean(self):
        cleaned = super().clean()
        if not Person.objects.filter(identificador=cleaned['cedula']).exists():
            self._errors['error'] = self._errors.get('error', self.error_class())
            self._errors['error'].append('No existe usuario registrado con esa cedula')
            # raise forms.ValidationError('No existe usuario registrado con esa cedula')
        return cleaned

    def get_user(self):
        cedula= self.cleaned_data.get('cedula')
        return Person.objects.get(identificador=cedula)

class ChangePasswordForm(forms.Form):
    clave = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Ingrese la contraseña nueva',
        'class':'form-control',
        'autocomplete':'off'
    }),label='Contraseña Nueva')

    claveconf = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Repita la contraseña',
        'class':'form-control',
        'autocomplete':'off'
    }),label='Repetir contraseña')

    def clean(self):
        cleaned = super().clean()
        clave = cleaned['clave']
        claveconf = cleaned['claveconf']
        if clave != claveconf:
            raise forms.ValidationError('Las contraseñas deben coincidir')
        return cleaned

class FormCampos(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(FormCampos, self).__init__(*args, **kwargs)

        #for visible in self.visible_fields():
        #    self.fields['grupo'].widget.attrs['class'] = "duallistbox"
        #    visible.field.widget.attrs['class'] = ' form-control  form-row '
        #    self.fields['titulo'].widget.attrs['class'] = 'form-control solo-letra'

    class Meta:
        model = TypeSector
        fields = '__all__'
        exclude = ("create_user", "modify_user","status","create_datetime","update_datetime")
