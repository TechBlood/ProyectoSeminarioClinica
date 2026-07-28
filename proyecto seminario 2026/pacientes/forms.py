from django import forms

from .models import TipoEstudio


class AgendarCitaForm(forms.Form):
    dpi = forms.CharField(label='DPI', max_length=20)
    nombre = forms.CharField(max_length=100)
    apellido = forms.CharField(max_length=100)
    telefono = forms.CharField(max_length=20, required=False)
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    tipo_estudio = forms.ModelChoiceField(queryset=TipoEstudio.objects.order_by('nombre'))
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    hora = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    notas = forms.CharField(widget=forms.Textarea, required=False)
