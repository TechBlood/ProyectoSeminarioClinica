import re

from django import forms
from django.utils import timezone

from accounts.models import Usuario

from .models import Paciente, Ticket, TipoEstudio

NOMBRE_REGEX = re.compile(r'^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]+$')


def validar_fecha_nacimiento_no_futura(fecha):
    if fecha and fecha > timezone.localdate():
        raise forms.ValidationError('La fecha de nacimiento no puede ser una fecha futura.')


class AgendarCitaForm(forms.Form):
    dpi = forms.CharField(
        label='DPI',
        max_length=13,
        min_length=13,
        widget=forms.TextInput(attrs={
            'maxlength': 13,
            'inputmode': 'numeric',
            'pattern': r'\d{13}',
            'title': 'El DPI debe tener exactamente 13 dígitos.',
        }),
    )
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'pattern': r'[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]+',
            'title': 'Solo letras y espacios.',
        }),
    )
    apellido = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'pattern': r'[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]+',
            'title': 'Solo letras y espacios.',
        }),
    )
    sexo = forms.ChoiceField(choices=Paciente.SEXO_CHOICES)
    telefono = forms.CharField(max_length=20, required=False)

    correo = forms.EmailField(
    label='Correo electrónico',
    max_length=254,
    required=True,
    widget=forms.EmailInput(attrs={
        'placeholder': 'paciente@correo.com',
        'autocomplete': 'email',
        }),
    )
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    tipo_estudio = forms.ModelChoiceField(
        queryset=TipoEstudio.objects.filter(activo=True).order_by('nombre')
    )
    radiologo = forms.ModelChoiceField(
        label='Radiólogo asignado',
        queryset=Usuario.objects.filter(
            rol=Usuario.ROL_MEDICO_RADIOLOGO, is_active=True
        ).order_by('username'),
    )
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    hora = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    notas = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_nacimiento'].widget.attrs['max'] = timezone.localdate().isoformat()

    def clean_dpi(self):
        dpi = self.cleaned_data['dpi'].strip()
        if not dpi.isdigit():
            raise forms.ValidationError('El DPI debe contener solo números.')
        if len(dpi) != 13:
            raise forms.ValidationError('El DPI debe tener exactamente 13 dígitos.')
        return dpi

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if not NOMBRE_REGEX.match(nombre):
            raise forms.ValidationError('El nombre solo puede contener letras y espacios.')
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data['apellido'].strip()
        if not NOMBRE_REGEX.match(apellido):
            raise forms.ValidationError('El apellido solo puede contener letras y espacios.')
        return apellido

    def clean_correo(self):
        return self.cleaned_data['correo'].strip().lower()
    

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data['fecha_nacimiento']
        validar_fecha_nacimiento_no_futura(fecha)
        return fecha


class RegistrarTicketForm(forms.Form):
    """Check-in de un paciente que llega sin cita (HU: Registrar Ticket,
    pantalla de Emergencia IGSS). Si el DPI ya existe se reutiliza ese
    paciente; si no, se registra con los datos capturados aquí."""

    dpi = forms.CharField(
        label='DPI',
        max_length=13,
        min_length=13,
        widget=forms.TextInput(attrs={
            'maxlength': 13,
            'inputmode': 'numeric',
            'pattern': r'\d{13}',
            'title': 'El DPI debe tener exactamente 13 dígitos.',
        }),
    )
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'pattern': r'[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]+',
            'title': 'Solo letras y espacios.',
        }),
    )
    apellido = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'pattern': r'[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]+',
            'title': 'Solo letras y espacios.',
        }),
    )
    sexo = forms.ChoiceField(choices=Paciente.SEXO_CHOICES)
    telefono = forms.CharField(max_length=20, required=False)
    correo = forms.EmailField(
    label='Correo electrónico',
    max_length=254,
    required=True,
    widget=forms.EmailInput(attrs={
        'placeholder': 'paciente@correo.com',
        'autocomplete': 'email',
     }),
    )

    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    prioridad = forms.ChoiceField(
        choices=Ticket.PRIORIDAD_CHOICES,
        initial=Ticket.PRIORIDAD_NORMAL,
        label='Prioridad',
    )
    motivo = forms.CharField(
        label='Motivo de la visita',
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_nacimiento'].widget.attrs['max'] = timezone.localdate().isoformat()

    def clean_dpi(self):
        dpi = self.cleaned_data['dpi'].strip()
        if not dpi.isdigit():
            raise forms.ValidationError('El DPI debe contener solo números.')
        if len(dpi) != 13:
            raise forms.ValidationError('El DPI debe tener exactamente 13 dígitos.')
        return dpi

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if not NOMBRE_REGEX.match(nombre):
            raise forms.ValidationError('El nombre solo puede contener letras y espacios.')
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data['apellido'].strip()
        if not NOMBRE_REGEX.match(apellido):
            raise forms.ValidationError('El apellido solo puede contener letras y espacios.')
        return apellido

    def clean_correo(self):
        return self.cleaned_data['correo'].strip().lower()


    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data['fecha_nacimiento']
        validar_fecha_nacimiento_no_futura(fecha)
        return fecha


class ProcesarTicketForm(forms.Form):
    """Convierte un ticket en espera directamente en una orden de trabajo
    para el técnico (se salta la revisión del radiólogo: el paciente ya
    está físicamente en la clínica por emergencia)."""

    tipo_estudio = forms.ModelChoiceField(
        queryset=TipoEstudio.objects.filter(activo=True).order_by('nombre'),
        label='Tipo de estudio',
    )
    motivo = forms.CharField(
        label='Motivo / indicación clínica',
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text='Ej: Paciente presenta dolor torácico agudo.',
    )


class CrearTipoEstudioForm(forms.ModelForm):
    class Meta:
        model = TipoEstudio
        fields = ('nombre', 'precio')

    def clean_precio(self):
        precio = self.cleaned_data['precio']
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0.')
        return precio


class GenerarOrdenForm(forms.Form):
    motivo = forms.CharField(
        label='Motivo / indicación clínica',
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text='Ej: Paciente presenta lesiones graves en el brazo izquierdo.',
    )


EXTENSIONES_IMAGEN_VALIDAS = ('.jpg', '.jpeg', '.png', '.dcm')


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return [single_file_clean(data, initial)] if data else []


class AdjuntarImagenesForm(forms.Form):
    imagenes = MultipleFileField(
        label='Imágenes del estudio',
        help_text='Formatos permitidos: JPG, PNG o DICOM (.dcm). Puedes seleccionar varias.',
    )

    def clean_imagenes(self):
        archivos = self.cleaned_data['imagenes']
        for archivo in archivos:
            if not archivo.name.lower().endswith(EXTENSIONES_IMAGEN_VALIDAS):
                raise forms.ValidationError(
                    f'"{archivo.name}" no es un formato válido (JPG, PNG o DCM).'
                )
        return archivos


class AdjuntarInformeForm(forms.Form):
    informe_texto = forms.CharField(
        label='Informe (texto)',
        widget=forms.Textarea(attrs={'rows': 8}),
        required=False,
    )
    informe_archivo = forms.FileField(
        label='Informe (PDF)',
        required=False,
    )

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('informe_texto') and not cleaned.get('informe_archivo'):
            raise forms.ValidationError(
                'Escribe el informe, adjunta un archivo, o ambos.'
            )
        archivo = cleaned.get('informe_archivo')
        if archivo and not archivo.name.lower().endswith('.pdf'):
            raise forms.ValidationError('El archivo adjunto debe ser un PDF.')
        return cleaned
