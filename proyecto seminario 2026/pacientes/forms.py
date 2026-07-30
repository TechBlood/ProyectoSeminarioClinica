from django import forms

from .models import TipoEstudio, Paciente


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


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['dpi', 'nombre', 'apellido', 'telefono', 'fecha_nacimiento', 'expediente']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'})
        }


class PacienteSearchForm(forms.Form):
    q = forms.CharField(label='DPI, nombre o expediente', required=False)


class CancelarCitaForm(forms.Form):
    motivo = forms.CharField(widget=forms.Textarea, required=True, label='Motivo de cancelación/reprogramación')
    nueva_fecha = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    nueva_hora = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
