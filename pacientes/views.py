import datetime

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date

from accounts.models import Usuario

from .forms import (
    AgendarCitaForm,
    CancelarCitaForm,
    PacienteForm,
    PacienteSearchForm,
    TicketActualizarForm,
    CheckInRecepcionForm,
)
from .horarios import CUPO_POR_HORA, DIAS_SEMANA, horas_disponibles, inicio_semana
from .models import CambioCita, Cita, Paciente, Ticket, TicketCambioEstado
from django.shortcuts import get_object_or_404
from django.db.models import Q


def es_recepcionista(user):
    return user.is_authenticated and user.rol == Usuario.ROL_RECEPCIONISTA


def es_recepcionista_o_admin(user):
    return user.is_authenticated and user.rol in {
        Usuario.ROL_RECEPCIONISTA,
        Usuario.ROL_ADMINISTRADOR,
    }


def crear_ticket_emergencia(paciente, cita, prioridad, estado=Ticket.ESTADO_EN_ESPERA):
    if not cita or cita.convenio != Cita.CONVENIO_EMERGENCIA_IGSS:
        return None
    return Ticket.objects.create(
        paciente=paciente,
        cita=cita,
        servicio=Ticket.SERVICIO_EMERGENCIA,
        prioridad=prioridad,
        estado=estado,
        hora_llegada=timezone.now(),
    )


@login_required
@user_passes_test(es_recepcionista_o_admin)
def seleccionar_horario(request, convenio):
    convenio_nombre = dict(Cita.CONVENIO_CHOICES).get(convenio, convenio)

    semana_param = parse_date(request.GET.get('semana', ''))
    inicio = inicio_semana(semana_param or datetime.date.today())
    dias = [inicio + datetime.timedelta(days=i) for i in range(len(DIAS_SEMANA))]
    # inicio_actual representa el inicio de la semana actual para el usuario (no permitir agendar semanas previas)
    inicio_actual = inicio_semana(datetime.date.today())

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
        'inicio_actual': inicio_actual,
    })


@login_required
@user_passes_test(es_recepcionista_o_admin)
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

        paciente, creado = Paciente.objects.get_or_create(
            dpi=cd['dpi'],
            defaults={
                'nombre': cd['nombre'],
                'apellido': cd['apellido'],
                'telefono': cd['telefono'],
                'fecha_nacimiento': cd['fecha_nacimiento'],
            },
        )
        if not creado:
            updated = False
            if not paciente.fecha_nacimiento:
                paciente.fecha_nacimiento = cd['fecha_nacimiento']
                updated = True
            if not paciente.telefono and cd['telefono']:
                paciente.telefono = cd['telefono']
                updated = True
            if updated:
                paciente.save()
        cita = Cita.objects.create(
            paciente=paciente,
            tipo_estudio=cd['tipo_estudio'],
            convenio=convenio,
            fecha=cd['fecha'],
            hora=cd['hora'],
            notas=cd['notas'],
            creada_por=request.user,
        )
        crear_ticket_emergencia(
            paciente=paciente,
            cita=cita,
            prioridad=Ticket.PRIORIDAD_EMERGENCIA,
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
@user_passes_test(es_recepcionista_o_admin)
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
@user_passes_test(es_recepcionista_o_admin)
def buscar_paciente(request):
    """Mostrar búsqueda de pacientes. Si no se suministra query, listar todos."""
    form = PacienteSearchForm(request.GET or None)
    pacientes = Paciente.objects.all().order_by('apellido', 'nombre')
    if form.is_valid():
        q = form.cleaned_data.get('q')
        if q:
            pacientes = pacientes.filter(
                Q(dpi__icontains=q)
                | Q(nombre__icontains=q)
                | Q(apellido__icontains=q)
                | Q(expediente__icontains=q)
                | Q(expediente_igss__icontains=q)
            )
    return render(request, 'pacientes/buscar_paciente.html', {'form': form, 'pacientes': pacientes})


@login_required
@user_passes_test(es_recepcionista_o_admin)
def listar_citas_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    citas = Cita.objects.filter(paciente=paciente).order_by('fecha', 'hora')
    return render(request, 'pacientes/listar_citas_paciente.html', {'paciente': paciente, 'citas': citas})


# Editar paciente
@login_required
@user_passes_test(es_recepcionista_o_admin)
def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, pk=paciente_id)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos del paciente actualizados.')
            return redirect('buscar_paciente')
    else:
        initial = {}
        if getattr(paciente, 'fecha_nacimiento', None):
            # ensure date input gets YYYY-MM-DD
            initial['fecha_nacimiento'] = paciente.fecha_nacimiento.isoformat()
        form = PacienteForm(instance=paciente, initial=initial)
    return render(request, 'pacientes/editar_paciente.html', {'form': form, 'paciente': paciente})


@login_required
@user_passes_test(es_recepcionista_o_admin)
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


@login_required
@user_passes_test(es_recepcionista_o_admin)
def pantalla_turnos(request):
    cola = Ticket.objects.filter(estado=Ticket.ESTADO_EN_ESPERA).order_by('-prioridad', 'hora_llegada')
    siguiente = cola.first()
    return render(request, 'pacientes/pantalla_turnos.html', {
        'cola': cola,
        'siguiente': siguiente,
    })


@login_required
@user_passes_test(es_recepcionista_o_admin)
def pantalla_turnos_json(request):
    cola = Ticket.objects.filter(estado=Ticket.ESTADO_EN_ESPERA).order_by('-prioridad', 'hora_llegada')
    datos = [
        {
            'id': ticket.id,
            'turno': ticket.turno,
            'paciente': str(ticket.paciente) if ticket.paciente else 'Paciente desconocido',
            'servicio': ticket.get_servicio_display(),
            'prioridad': ticket.get_prioridad_display(),
            'hora_llegada': ticket.hora_llegada.isoformat() if ticket.hora_llegada else None,
        }
        for ticket in cola
    ]
    return JsonResponse({'cola': datos})


@login_required
@user_passes_test(es_recepcionista_o_admin)
def actualizar_estado_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    if request.method == 'POST':
        form = TicketActualizarForm(request.POST)
        if form.is_valid():
            estado_anterior = ticket.estado
            prioridad_anterior = ticket.prioridad
            ticket.estado = form.cleaned_data['estado']
            ticket.prioridad = int(form.cleaned_data['prioridad'])
            razon = form.cleaned_data['razon']
            now = timezone.now()
            if ticket.estado == Ticket.ESTADO_EN_PROCESO and not ticket.hora_llamado:
                ticket.hora_llamado = now
            if ticket.estado == Ticket.ESTADO_COMPLETADO and not ticket.hora_fin_estudio:
                ticket.hora_fin_estudio = now
            if ticket.estado == Ticket.ESTADO_AUSENTE and not ticket.hora_fin_estudio:
                ticket.hora_fin_estudio = now
            ticket.save()
            TicketCambioEstado.objects.create(
                ticket=ticket,
                estado_anterior=estado_anterior,
                estado_nuevo=ticket.estado,
                prioridad_anterior=prioridad_anterior,
                prioridad_nueva=ticket.prioridad,
                razon=razon,
                usuario=request.user,
            )
            messages.success(request, 'Estado de ticket actualizado correctamente.')
            return redirect('pantalla_turnos')
    else:
        form = TicketActualizarForm(initial={
            'estado': ticket.estado,
            'prioridad': ticket.prioridad,
        })
    return render(request, 'pacientes/actualizar_estado_ticket.html', {'form': form, 'ticket': ticket})


# Cancelar o reprogramar cita y registrar motivo
@login_required
@user_passes_test(es_recepcionista_o_admin)
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


# HU-023: Registro de llegada y atención inicial de paciente (Check-in en recepción)
@login_required
@user_passes_test(es_recepcionista_o_admin)
def check_in_recepcion(request):
    """Módulo de recepción para registrar llegada de paciente y crear/actualizar ticket"""
    paciente_encontrado = None
    tickets_paciente = []
    
    if request.method == 'POST':
        form = CheckInRecepcionForm(request.POST)
        if form.is_valid():
            criterio = form.cleaned_data['criterio_busqueda'].strip()
            prioridad = int(form.cleaned_data.get('prioridad', Ticket.PRIORIDAD_NORMAL))
            
            # Buscar paciente por DPI, expediente o nombre
            paciente = Paciente.objects.filter(
                Q(dpi__iexact=criterio) |
                Q(expediente__iexact=criterio) |
                Q(nombre__icontains=criterio)
            ).first()
            
            if paciente:
                paciente_encontrado = paciente
                # Obtener tickets activos del paciente
                tickets_paciente = Ticket.objects.filter(
                    paciente=paciente,
                    estado=Ticket.ESTADO_EN_ESPERA
                ).order_by('-prioridad', 'hora_llegada')
                
                # Si no hay ticket en espera, crear uno nuevo
                if not tickets_paciente.exists():
                    cita = Cita.objects.filter(
                        paciente=paciente,
                        estado=Cita.ESTADO_AGENDADA,
                        fecha__gte=timezone.now().date()
                    ).first()

                    ticket = crear_ticket_emergencia(
                        paciente=paciente,
                        cita=cita,
                        prioridad=prioridad,
                    )

                    if ticket:
                        messages.success(
                            request,
                            f'Paciente {paciente.nombre} {paciente.apellido} registrado en recepción. Ticket: {ticket.turno}'
                        )
                        tickets_paciente = [ticket]
                    else:
                        messages.info(request, 'No se generó ticket porque la cita no corresponde a Emergencia IGSS.')
                else:
                    # Actualizar prioridad del ticket existente si cambió
                    ticket_actual = tickets_paciente.first()
                    if ticket_actual.prioridad != prioridad:
                        ticket_anterior = ticket_actual.prioridad
                        ticket_actual.prioridad = prioridad
                        ticket_actual.save()
                        TicketCambioEstado.objects.create(
                            ticket=ticket_actual,
                            estado_anterior=ticket_actual.estado,
                            estado_nuevo=ticket_actual.estado,
                            prioridad_anterior=ticket_anterior,
                            prioridad_nueva=prioridad,
                            razon='Ajuste de prioridad en recepción',
                            usuario=request.user,
                        )
                        messages.info(request, f'Prioridad actualizada a {ticket_actual.get_prioridad_display()}')
                    else:
                        messages.info(request, 'Paciente ya registrado en recepción.')
            else:
                messages.error(request, 'No se encontró paciente con ese criterio de búsqueda.')
    else:
        form = CheckInRecepcionForm()
    
    return render(request, 'pacientes/check_in_recepcion.html', {
        'form': form,
        'paciente_encontrado': paciente_encontrado,
        'tickets_paciente': tickets_paciente,
    })
