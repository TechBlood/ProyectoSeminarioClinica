from django import forms

from .models import TipoEstudio, Paciente, Ticket, validar_dpi_guatemala, validar_nombre_apellido


class AgendarCitaForm(forms.Form):
    dpi = forms.CharField(label='DPI', max_length=20, validators=[validar_dpi_guatemala])
    nombre = forms.CharField(max_length=100, validators=[validar_nombre_apellido])
    apellido = forms.CharField(max_length=100, validators=[validar_nombre_apellido])
    telefono = forms.CharField(max_length=20, required=False)
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    tipo_estudio = forms.ModelChoiceField(queryset=TipoEstudio.objects.order_by('nombre'))
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    hora = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    notas = forms.CharField(widget=forms.Textarea, required=False)


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['dpi', 'nombre', 'apellido', 'telefono', 'fecha_nacimiento', 'expediente_igss']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'})
        }


class PacienteSearchForm(forms.Form):
    q = forms.CharField(label='DPI, nombre o expediente', required=False)


class CancelarCitaForm(forms.Form):
    motivo = forms.CharField(widget=forms.Textarea, required=True, label='Motivo de cancelación/reprogramación')
    nueva_fecha = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    nueva_hora = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))


class TicketActualizarForm(forms.Form):
    estado = forms.ChoiceField(choices=Ticket.ESTADO_CHOICES, label='Estado del ticket')
    prioridad = forms.ChoiceField(choices=Ticket.PRIORIDAD_CHOICES, label='Prioridad del ticket')
    razon = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, label='Motivo / nota')
