import datetime

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date

from accounts.models import Usuario

from .forms import AgendarCitaForm, PacienteForm, PacienteSearchForm, CancelarCitaForm
from .horarios import CUPO_POR_HORA, DIAS_SEMANA, horas_disponibles, inicio_semana
from .models import Cita, Paciente, CambioCita
from django.shortcuts import get_object_or_404
from django.db.models import Q


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


# Registro de paciente independiente
@login_required
@user_passes_test(es_recepcionista)
def registrar_paciente(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paciente registrado correctamente.')
            return redirect('buscar_paciente')
    else:
        form = PacienteForm()
    return render(request, 'pacientes/registrar_paciente.html', {'form': form})


# Búsqueda y listado de pacientes
@login_required
@user_passes_test(es_recepcionista)
def buscar_paciente(request):
    """Mostrar búsqueda de pacientes. Si no se suministra query, listar todos."""
    form = PacienteSearchForm(request.GET or None)
    pacientes = Paciente.objects.all().order_by('apellido', 'nombre')
    if form.is_valid():
        q = form.cleaned_data.get('q')
        if q:
            pacientes = pacientes.filter(
                Q(dpi__icontains=q) | Q(nombre__icontains=q) | Q(expediente__icontains=q)
            )
    return render(request, 'pacientes/buscar_paciente.html', {'form': form, 'pacientes': pacientes})


@login_required
@user_passes_test(es_recepcionista)
def listar_citas_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    citas = Cita.objects.filter(paciente=paciente).order_by('fecha', 'hora')
    return render(request, 'pacientes/listar_citas_paciente.html', {'paciente': paciente, 'citas': citas})


# Editar paciente
@login_required
@user_passes_test(es_recepcionista)
def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos del paciente actualizados.')
            return redirect('buscar_paciente')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'pacientes/editar_paciente.html', {'form': form, 'paciente': paciente})


@login_required
@user_passes_test(es_recepcionista)
def procesar_cita_coex(request):
    form = PacienteSearchForm(request.GET or None)
    citas = Cita.objects.filter(convenio=Cita.CONVENIO_COEX).select_related('paciente').order_by('fecha', 'hora')
    if form.is_valid():
        q = form.cleaned_data.get('q')
        if q:
            citas = citas.filter(
                Q(paciente__dpi__icontains=q) |
                Q(paciente__nombre__icontains=q) |
                Q(paciente__apellido__icontains=q) |
                Q(paciente__expediente__icontains=q)
            )
    return render(request, 'pacientes/procesar_cita_coex.html', {'form': form, 'citas': citas})


# Cancelar o reprogramar cita y registrar motivo
@login_required
@user_passes_test(es_recepcionista)
def cancelar_cita(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)
    if request.method == 'POST':
        form = CancelarCitaForm(request.POST)
        if form.is_valid():
            motivo = form.cleaned_data['motivo']
            nueva_fecha = form.cleaned_data.get('nueva_fecha')
            nueva_hora = form.cleaned_data.get('nueva_hora')
            if nueva_fecha and nueva_hora:
                # reprogramación
                CambioCita.objects.create(
                    cita=cita,
                    accion=CambioCita.ACCION_REPROGRAMAR,
                    motivo=motivo,
                    usuario=request.user,
                )
                cita.fecha = nueva_fecha
                cita.hora = nueva_hora
                cita.estado = Cita.ESTADO_AGENDADA
                cita.save()
                messages.success(request, 'Cita reprogramada correctamente.')
            else:
                # cancelación
                CambioCita.objects.create(
                    cita=cita,
                    accion=CambioCita.ACCION_CANCELAR,
                    motivo=motivo,
                    usuario=request.user,
                )
                cita.estado = Cita.ESTADO_CANCELADA
                cita.save()
                messages.success(request, 'Cita cancelada y motivo registrado.')
            return redirect('calendario_coex')
    else:
        form = CancelarCitaForm()
    return render(request, 'pacientes/cancelar_cita.html', {'form': form, 'cita': cita})
