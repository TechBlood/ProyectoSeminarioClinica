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

    def clean(self):
        cleaned = super().clean()
        dpi = cleaned.get('dpi')
        telefono = cleaned.get('telefono')
        # DPI validator already enforces format; prevent phone being used by other patient
        if telefono:
            qs = Paciente.objects.filter(telefono=telefono)
            if qs.exists():
                # if dpi exists and belongs to same patient it's probably ok; otherwise block
                if not qs.filter(dpi=dpi).exists():
                    raise forms.ValidationError('El teléfono ya está registrado para otro paciente.')
        return cleaned


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['dpi', 'nombre', 'apellido', 'telefono', 'fecha_nacimiento', 'expediente_igss']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing existing instance, ensure fecha_nacimiento is rendered as ISO date value
        if self.instance and getattr(self.instance, 'fecha_nacimiento', None):
            fecha = self.instance.fecha_nacimiento
            self.initial.setdefault('fecha_nacimiento', fecha.isoformat())

    def clean_dpi(self):
        dpi = self.cleaned_data.get('dpi') or ''
        validar_dpi_guatemala(dpi)
        # ensure unique DPI (unless it's the same instance)
        qs = Paciente.objects.filter(dpi=dpi)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un paciente con ese DPI.')
        return dpi

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre') or ''
        validar_nombre_apellido(nombre)
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido') or ''
        validar_nombre_apellido(apellido)
        return apellido

    def clean(self):
        cleaned = super().clean()
        # fecha_nacimiento must be present and a valid date (DateField handles format)
        if not cleaned.get('fecha_nacimiento'):
            raise forms.ValidationError('La fecha de nacimiento es obligatoria.')
        return cleaned


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


class CheckInRecepcionForm(forms.Form):
    """Formulario para check-in de pacientes en recepción (HU-023)"""
    criterio_busqueda = forms.CharField(
        label='DPI, expediente o nombre del paciente',
        max_length=100,
        required=True
    )
    prioridad = forms.ChoiceField(
        choices=Ticket.PRIORIDAD_CHOICES,
        label='Prioridad del paciente',
        initial=Ticket.PRIORIDAD_NORMAL,
        required=False
    )
