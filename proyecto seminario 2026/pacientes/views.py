import datetime

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date

from accounts.models import Usuario

from .forms import AgendarCitaForm
from .horarios import CUPO_POR_HORA, DIAS_SEMANA, horas_disponibles, inicio_semana
from .models import Cita, Paciente


def es_recepcionista(user):
    return user.is_authenticated and user.rol == Usuario.ROL_RECEPCIONISTA


@login_required
@user_passes_test(es_recepcionista)
def seleccionar_horario(request, convenio):
    convenio_nombre = dict(Cita.CONVENIO_CHOICES).get(convenio, convenio)

    semana_param = parse_date(request.GET.get('semana', ''))
    inicio = inicio_semana(semana_param or datetime.date.today())
    dias = [inicio + datetime.timedelta(days=i) for i in range(len(DIAS_SEMANA))]

    conteos = {}
    for cita in Cita.objects.filter(fecha__gte=dias[0], fecha__lte=dias[-1]):
        clave = (cita.fecha, cita.hora.hour)
        conteos[clave] = conteos.get(clave, 0) + 1

    filas = [
        {
            'hora': hora,
            'celdas': [
                {
                    'dia': dia,
                    'hora': hora,
                    'cantidad': conteos.get((dia, hora), 0),
                    'lleno': conteos.get((dia, hora), 0) >= CUPO_POR_HORA,
                }
                for dia in dias
            ],
        }
        for hora in horas_disponibles()
    ]

    return render(request, 'pacientes/calendario.html', {
        'convenio_nombre': convenio_nombre,
        'agendar_url_name': f'agendar_cita_{convenio}',
        'dias': list(zip(DIAS_SEMANA, dias)),
        'filas': filas,
        'cupo': CUPO_POR_HORA,
        'semana_anterior': inicio - datetime.timedelta(days=7),
        'semana_siguiente': inicio + datetime.timedelta(days=7),
    })


@login_required
@user_passes_test(es_recepcionista)
def agendar_cita(request, convenio):
    convenio_nombre = dict(Cita.CONVENIO_CHOICES).get(convenio, convenio)
    calendario_url = reverse(f'calendario_{convenio}')

    datos = request.POST if request.method == 'POST' else request.GET
    fecha = datos.get('fecha')
    hora = datos.get('hora')
    if not fecha or not hora:
        return redirect(calendario_url)

    if request.method == 'POST':
        form = AgendarCitaForm(request.POST)
    else:
        form = AgendarCitaForm(initial={'fecha': fecha, 'hora': hora})
    form.fields['fecha'].widget = forms.HiddenInput()
    form.fields['hora'].widget = forms.HiddenInput()

    if request.method == 'POST' and form.is_valid():
        cd = form.cleaned_data
        cupo_actual = Cita.objects.filter(fecha=cd['fecha'], hora__hour=cd['hora'].hour).count()
        if cupo_actual >= CUPO_POR_HORA:
            messages.error(request, 'Ese horario ya se llenó, elige otro.')
            return redirect(calendario_url)

        paciente, _ = Paciente.objects.get_or_create(
            dpi=cd['dpi'],
            defaults={
                'nombre': cd['nombre'],
                'apellido': cd['apellido'],
                'telefono': cd['telefono'],
                'fecha_nacimiento': cd['fecha_nacimiento'],
            },
        )
        Cita.objects.create(
            paciente=paciente,
            tipo_estudio=cd['tipo_estudio'],
            convenio=convenio,
            fecha=cd['fecha'],
            hora=cd['hora'],
            notas=cd['notas'],
            creada_por=request.user,
        )
        messages.success(
            request,
            f'Cita agendada para {paciente.nombre} {paciente.apellido} el {cd["fecha"]} a las {cd["hora"]}.',
        )
        return redirect('dashboard')

    return render(request, 'pacientes/agendar_cita.html', {
        'form': form,
        'convenio_nombre': convenio_nombre,
        'calendario_url': calendario_url,
        'fecha_valor': fecha,
        'hora_valor': hora,
    })
