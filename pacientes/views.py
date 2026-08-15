import datetime

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.dateparse import parse_date

from accounts.models import Bitacora, Usuario
from accounts.views import es_administrador

from .forms import (
    AdjuntarImagenesForm,
    AdjuntarInformeForm,
    AgendarCitaForm,
    CrearTipoEstudioForm,
    GenerarOrdenForm,
    ProcesarTicketForm,
    RegistrarTicketForm,
)
from .horarios import (
    DIAS_SEMANA,
    LIMITE_DIAS_ADELANTE,
    en_el_pasado,
    fuera_de_ventana,
    horas_disponibles,
    inicio_semana,
)
from .models import Cita, ImagenEstudio, Notificacion, OrdenTrabajo, Paciente, Ticket


def es_recepcionista(user):
    return user.is_authenticated and user.rol == Usuario.ROL_RECEPCIONISTA


def es_tecnico(user):
    return user.is_authenticated and user.rol == Usuario.ROL_TECNICO_IMAGENES


def es_radiologo(user):
    return user.is_authenticated and user.rol == Usuario.ROL_MEDICO_RADIOLOGO


def _notificar_cita_asignada(cita):
    """El radiólogo elegido al agendar la cita recibe una nueva solicitud
    para revisar/confirmar."""
    Notificacion.notificar(
        destinatario=cita.radiologo,
        tipo=Notificacion.TIPO_CITA_ASIGNADA,
        mensaje=(
            f'Nueva cita asignada: {cita.tipo_estudio} para {cita.paciente.nombre} '
            f'{cita.paciente.apellido} el {cita.fecha_sugerida or cita.fecha} a las '
            f'{cita.hora_sugerida or cita.hora}.'
        ),
        cita=cita,
        url=reverse('solicitudes_pendientes'),
    )


def _notificar_orden_pendiente(cita):
    """Aviso para el equipo de técnicos: hay una orden de trabajo nueva
    esperando que le tomen las imágenes."""
    tecnicos = Usuario.objects.filter(rol=Usuario.ROL_TECNICO_IMAGENES, is_active=True)
    Notificacion.notificar_a_varios(
        usuarios=tecnicos,
        tipo=Notificacion.TIPO_ORDEN_PENDIENTE,
        mensaje=(
            f'Nueva orden de trabajo: {cita.tipo_estudio} para {cita.paciente.nombre} '
            f'{cita.paciente.apellido}.'
        ),
        cita=cita,
        url=reverse('ordenes_pendientes'),
    )


def _notificar_estudio_listo_para_informar(cita):
    """Cuando el técnico termina de subir las imágenes, se avisa al
    radiólogo asignado (o a todo el equipo de radiología si la cita no
    tenía uno asignado, como los tickets de emergencia)."""
    if cita.radiologo_id:
        radiologos = [cita.radiologo]
    else:
        radiologos = Usuario.objects.filter(rol=Usuario.ROL_MEDICO_RADIOLOGO, is_active=True)
    Notificacion.notificar_a_varios(
        usuarios=radiologos,
        tipo=Notificacion.TIPO_ESTUDIO_LISTO_INFORMAR,
        mensaje=(
            f'Estudio listo para informar: {cita.tipo_estudio} de {cita.paciente.nombre} '
            f'{cita.paciente.apellido}.'
        ),
        cita=cita,
        url=reverse('citas_procesadas'),
    )


def _notificar_estudio_completado(cita):
    """Cuando el radiólogo termina el informe (diagnóstico), se avisa a
    todo el equipo de recepción para que puedan entregar el resultado."""
    try:
        url = reverse(f'procesar_citas_{cita.convenio}')
    except NoReverseMatch:
        # Todavía no existe una pantalla de "procesar citas" para este
        # convenio (por ahora solo COEX la tiene); igual se notifica, solo
        # que el enlace de la notificación cae al panel principal.
        url = reverse('dashboard')
    recepcionistas = Usuario.objects.filter(rol=Usuario.ROL_RECEPCIONISTA, is_active=True)
    Notificacion.notificar_a_varios(
        usuarios=recepcionistas,
        tipo=Notificacion.TIPO_ESTUDIO_COMPLETADO,
        mensaje=(
            f'Estudio completado: {cita.tipo_estudio} de {cita.paciente.nombre} {cita.paciente.apellido}. '
            'Informe y diagnóstico listos.'
        ),
        cita=cita,
        url=url,
    )


CAMPOS_DATOS_PACIENTE = ('nombre', 'apellido', 'sexo', 'telefono', 'fecha_nacimiento')


def obtener_o_actualizar_paciente(cd):
    """Reutiliza el paciente si el DPI ya existe (evita duplicar el registro)
    y sincroniza sus datos con lo capturado en el formulario, por si el
    recepcionista corrigió algo (ej. un teléfono desactualizado)."""
    paciente, creado = Paciente.objects.get_or_create(
        dpi=cd['dpi'],
        defaults={campo: cd[campo] for campo in CAMPOS_DATOS_PACIENTE},
    )
    if not creado:
        cambiados = [
            campo for campo in CAMPOS_DATOS_PACIENTE if getattr(paciente, campo) != cd[campo]
        ]
        if cambiados:
            for campo in cambiados:
                setattr(paciente, campo, cd[campo])
            paciente.save(update_fields=cambiados)
    return paciente


@login_required
@user_passes_test(es_recepcionista)
def buscar_paciente_por_dpi(request):
    """Usado por el formulario de agendar cita / registrar ticket para
    autocompletar los datos si el paciente ya está registrado, en vez de
    hacer que el recepcionista los vuelva a escribir."""
    dpi = (request.GET.get('dpi') or '').strip()
    paciente = Paciente.objects.filter(dpi=dpi).first() if dpi else None
    if not paciente:
        return JsonResponse({'encontrado': False})
    return JsonResponse({
        'encontrado': True,
        'nombre': paciente.nombre,
        'apellido': paciente.apellido,
        'sexo': paciente.sexo,
        'telefono': paciente.telefono,
        'fecha_nacimiento': (
            paciente.fecha_nacimiento.isoformat() if paciente.fecha_nacimiento else ''
        ),
    })


@login_required
@user_passes_test(es_administrador)
def crear_estudio(request):
    if request.method == 'POST':
        form = CrearTipoEstudioForm(request.POST)
        if form.is_valid():
            tipo_estudio = form.save()
            Bitacora.registrar(
                request=request,
                usuario=request.user,
                accion=Bitacora.ACCION_CREAR_ESTUDIO,
                descripcion=f'Creó el estudio "{tipo_estudio.nombre}" (precio: {tipo_estudio.precio}).',
            )
            messages.success(request, f'Estudio "{tipo_estudio.nombre}" creado correctamente.')
            return redirect('dashboard')
    else:
        form = CrearTipoEstudioForm()
    return render(request, 'pacientes/crear_estudio.html', {'form': form})


@login_required
@user_passes_test(es_recepcionista)
def seleccionar_horario(request, convenio):
    convenio_nombre = dict(Cita.CONVENIO_CHOICES).get(convenio, convenio)

    reagendar_cita = None
    reagendar_id = request.GET.get('reagendar')
    if reagendar_id:
        reagendar_cita = get_object_or_404(Cita, id=reagendar_id, convenio=convenio)

    hoy = datetime.date.today()
    semana_param = parse_date(request.GET.get('semana', ''))
    inicio = inicio_semana(semana_param or hoy)
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
                    'pasado': en_el_pasado(dia, datetime.time(hora, 0)),
                    'fuera_rango': fuera_de_ventana(dia),
                }
                for dia in dias
            ],
        }
        for hora in horas_disponibles()
    ]

    contexto = {
        'convenio': convenio,
        'convenio_nombre': convenio_nombre,
        'agendar_url_name': f'agendar_cita_{convenio}',
        'dias': list(zip(DIAS_SEMANA, dias)),
        'filas': filas,
        'semana_anterior': inicio - datetime.timedelta(days=7),
        'mostrar_semana_anterior': inicio > inicio_semana(hoy),
        'semana_siguiente': inicio + datetime.timedelta(days=7),
        'mostrar_semana_siguiente': not fuera_de_ventana(inicio + datetime.timedelta(days=7)),
        'reagendar_cita': reagendar_cita,
        'reagendar_url_name': f'confirmar_reagenda_{convenio}' if reagendar_cita else None,
        'procesar_url_name': f'procesar_citas_{convenio}',
    }
    return render(request, 'pacientes/calendario.html', contexto)


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
        if en_el_pasado(cd['fecha'], cd['hora']):
            messages.error(request, 'No se pueden agendar citas en un horario que ya pasó.')
            return redirect(calendario_url)
        if fuera_de_ventana(cd['fecha']):
            messages.error(request, 'Solo se pueden agendar citas hasta 3 semanas después de hoy.')
            return redirect(calendario_url)

        paciente = obtener_o_actualizar_paciente(cd)
        cita = Cita.objects.create(
            paciente=paciente,
            tipo_estudio=cd['tipo_estudio'],
            radiologo=cd['radiologo'],
            convenio=convenio,
            estado=Cita.ESTADO_PENDIENTE,
            fecha=cd['fecha'],
            hora=cd['hora'],
            fecha_sugerida=cd['fecha'],
            hora_sugerida=cd['hora'],
            notas=cd['notas'],
            creada_por=request.user,
        )
        _notificar_cita_asignada(cita)
        Bitacora.registrar(
            request=request,
            usuario=request.user,
            accion=Bitacora.ACCION_SOLICITAR_CITA,
            descripcion=(
                f'Registró al paciente {paciente.nombre} {paciente.apellido} (DPI {paciente.dpi}) '
                f'y solicitó cita de {cd["tipo_estudio"]} para {cd["fecha"]} {cd["hora"]} ({convenio}), '
                f'asignada a {cd["radiologo"]}.'
            ),
        )
        messages.success(
            request,
            f'Solicitud enviada a {cd["radiologo"]} para {paciente.nombre} {paciente.apellido} '
            f'(sugerido: {cd["fecha"]} a las {cd["hora"]}). '
            'Quedará agendada cuando la radióloga la confirme.',
        )
        return redirect('dashboard')

    return render(request, 'pacientes/agendar_cita.html', {
        'form': form,
        'convenio_nombre': convenio_nombre,
        'calendario_url': calendario_url,
        'fecha_valor': fecha,
        'hora_valor': hora,
    })


@login_required
@user_passes_test(es_recepcionista)
def procesar_citas(request, convenio):
    convenio_nombre = dict(Cita.CONVENIO_CHOICES).get(convenio, convenio)

    fecha = parse_date(request.GET.get('fecha', '')) or datetime.date.today()
    citas = (
        Cita.objects.filter(convenio=convenio, fecha=fecha)
        .exclude(estado=Cita.ESTADO_PENDIENTE)
        .select_related('paciente', 'tipo_estudio')
        .order_by('hora')
    )

    return render(request, 'pacientes/procesar_citas.html', {
        'convenio': convenio,
        'convenio_nombre': convenio_nombre,
        'fecha': fecha,
        'hoy': datetime.date.today(),
        'dia_anterior': fecha - datetime.timedelta(days=1),
        'dia_siguiente': fecha + datetime.timedelta(days=1),
        'citas': citas,
        'calendario_url_name': f'calendario_{convenio}',
        'marcar_llegada_url_name': f'marcar_llegada_{convenio}',
        'generar_orden_url_name': f'generar_orden_{convenio}',
        'marcar_ausente_url_name': f'marcar_ausente_{convenio}',
    })


@login_required
@user_passes_test(es_recepcionista)
def marcar_llegada(request, convenio, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, convenio=convenio)
    if request.method == 'POST' and cita.estado == Cita.ESTADO_AGENDADA:
        cita.hora_llegada = timezone.now()
        cita.save(update_fields=['hora_llegada'])
        Bitacora.registrar(
            request=request,
            usuario=request.user,
            accion=Bitacora.ACCION_MARCAR_LLEGADA,
            descripcion=f'Marcó la llegada de {cita.paciente} (cita #{cita.id}).',
        )
        messages.success(request, f'Se registró la llegada de {cita.paciente}.')
    return redirect(f'{reverse(f"procesar_citas_{convenio}")}?fecha={cita.fecha}')


@login_required
@user_passes_test(es_recepcionista)
def generar_orden(request, convenio, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, convenio=convenio)
    volver_url = f'{reverse(f"procesar_citas_{convenio}")}?fecha={cita.fecha}'

    if not cita.hora_llegada:
        messages.error(request, 'Primero hay que marcar la llegada del paciente.')
        return redirect(volver_url)
    if cita.estado != Cita.ESTADO_AGENDADA:
        messages.error(request, 'Esta cita ya no está pendiente de procesar.')
        return redirect(volver_url)

    if request.method == 'POST':
        form = GenerarOrdenForm(request.POST)
        if form.is_valid():
            OrdenTrabajo.objects.create(
                cita=cita,
                motivo=form.cleaned_data['motivo'],
                creada_por=request.user,
            )
            cita.estado = Cita.ESTADO_EN_PROCESO
            cita.save(update_fields=['estado'])
            _notificar_orden_pendiente(cita)
            Bitacora.registrar(
                request=request,
                usuario=request.user,
                accion=Bitacora.ACCION_GENERAR_ORDEN,
                descripcion=f'Generó la orden de trabajo para {cita.paciente} (cita #{cita.id}).',
            )
            messages.success(
                request, f'Orden de trabajo generada y enviada al técnico para {cita.paciente}.'
            )
            return redirect(volver_url)
    else:
        form = GenerarOrdenForm()

    return render(request, 'pacientes/generar_orden.html', {
        'form': form,
        'cita': cita,
        'edad': cita.paciente.edad_en(cita.fecha),
        'volver_url': volver_url,
    })


@login_required
@user_passes_test(es_tecnico)
def ordenes_pendientes(request):
    ordenes = (
        OrdenTrabajo.objects.filter(cita__estado=Cita.ESTADO_EN_PROCESO)
        .exclude(imagenes__isnull=False)
        .select_related('cita', 'cita__paciente', 'cita__tipo_estudio')
        .distinct()
        .order_by('creada_en')
    )
    return render(request, 'pacientes/ordenes_pendientes.html', {'ordenes': ordenes})


@login_required
@user_passes_test(es_tecnico)
def adjuntar_imagenes(request, orden_id):
    orden = get_object_or_404(OrdenTrabajo, id=orden_id, cita__estado=Cita.ESTADO_EN_PROCESO)
    volver_url = reverse('ordenes_pendientes')

    if request.method == 'POST':
        form = AdjuntarImagenesForm(request.POST, request.FILES)
        if form.is_valid():
            archivos = form.cleaned_data['imagenes']
            for archivo in archivos:
                ImagenEstudio.objects.create(orden=orden, archivo=archivo, subida_por=request.user)
            _notificar_estudio_listo_para_informar(orden.cita)
            Bitacora.registrar(
                request=request,
                usuario=request.user,
                accion=Bitacora.ACCION_ADJUNTAR_IMAGENES,
                descripcion=(
                    f'Adjuntó {len(archivos)} imagen(es) a la orden de {orden.cita.paciente} '
                    f'(orden #{orden.id}).'
                ),
            )
            messages.success(
                request, f'Imágenes adjuntadas para {orden.cita.paciente}. Ya está lista para la radióloga.'
            )
            return redirect(volver_url)
    else:
        form = AdjuntarImagenesForm()

    return render(request, 'pacientes/adjuntar_imagenes.html', {
        'form': form,
        'cita': orden.cita,
        'orden': orden,
        'edad': orden.edad_paciente,
        'volver_url': volver_url,
    })


@login_required
@user_passes_test(es_radiologo)
def citas_procesadas(request):
    ordenes = (
        OrdenTrabajo.objects.filter(cita__estado=Cita.ESTADO_EN_PROCESO, imagenes__isnull=False)
        .select_related('cita', 'cita__paciente', 'cita__tipo_estudio')
        .distinct()
        .order_by('creada_en')
    )
    return render(request, 'pacientes/citas_procesadas.html', {'ordenes': ordenes})


@login_required
@user_passes_test(es_radiologo)
def adjuntar_informe(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, estado=Cita.ESTADO_EN_PROCESO)
    orden = get_object_or_404(OrdenTrabajo, cita=cita)
    if not orden.tiene_imagenes:
        messages.error(request, 'El técnico todavía no adjunta las imágenes de este estudio.')
        return redirect('citas_procesadas')
    volver_url = reverse('citas_procesadas')

    if request.method == 'POST':
        form = AdjuntarInformeForm(request.POST, request.FILES)
        if form.is_valid():
            orden.informe_texto = form.cleaned_data['informe_texto']
            if form.cleaned_data['informe_archivo']:
                orden.informe_archivo = form.cleaned_data['informe_archivo']
            orden.informe_creado_por = request.user
            orden.informe_creado_en = timezone.now()
            orden.save(update_fields=[
                'informe_texto', 'informe_archivo', 'informe_creado_por', 'informe_creado_en',
            ])
            cita.estado = Cita.ESTADO_PROCESADA
            cita.save(update_fields=['estado'])
            _notificar_estudio_completado(cita)
            Bitacora.registrar(
                request=request,
                usuario=request.user,
                accion=Bitacora.ACCION_ADJUNTAR_INFORME,
                descripcion=f'Adjuntó el informe de {cita.paciente} (cita #{cita.id}).',
            )
            messages.success(request, f'Informe adjuntado para {cita.paciente}.')
            return redirect(volver_url)
    else:
        form = AdjuntarInformeForm()

    return render(request, 'pacientes/adjuntar_informe.html', {
        'form': form,
        'cita': cita,
        'orden': orden,
        'edad': cita.paciente.edad_en(cita.fecha),
        'volver_url': volver_url,
    })


@login_required
@user_passes_test(es_radiologo)
def solicitudes_pendientes(request):
    citas = (
        Cita.objects.filter(estado=Cita.ESTADO_PENDIENTE, radiologo=request.user)
        .select_related('paciente', 'tipo_estudio')
        .order_by('fecha_sugerida', 'hora_sugerida')
    )
    return render(request, 'pacientes/solicitudes_pendientes.html', {'citas': citas})


@login_required
@user_passes_test(es_radiologo)
def revisar_solicitud(request, cita_id):
    cita = get_object_or_404(
        Cita, id=cita_id, estado=Cita.ESTADO_PENDIENTE, radiologo=request.user
    )
    volver_url = reverse('solicitudes_pendientes')
    limite = cita.creada_en.date() + datetime.timedelta(days=LIMITE_DIAS_ADELANTE)

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'rechazar':
            cita.estado = Cita.ESTADO_RECHAZADA
            cita.motivo_rechazo = request.POST.get('motivo_rechazo', '').strip()
            cita.revisada_por = request.user
            cita.revisada_en = timezone.now()
            cita.save(update_fields=['estado', 'motivo_rechazo', 'revisada_por', 'revisada_en'])
            Bitacora.registrar(
                request=request,
                usuario=request.user,
                accion=Bitacora.ACCION_RECHAZAR_CITA,
                descripcion=(
                    f'Rechazó la solicitud de cita de {cita.paciente} (cita #{cita.id}). '
                    f'Motivo: {cita.motivo_rechazo or "—"}'
                ),
            )
            messages.success(request, f'Solicitud de {cita.paciente} rechazada.')
            return redirect(volver_url)

        fecha = parse_date(request.POST.get('fecha', ''))
        hora_str = request.POST.get('hora', '')
        try:
            hora = datetime.datetime.strptime(hora_str, '%H:%M').time()
        except ValueError:
            hora = None

        if not fecha or not hora:
            messages.error(request, 'Fecha u hora inválida.')
            return redirect(request.path)
        if en_el_pasado(fecha, hora):
            messages.error(request, 'No se puede confirmar una cita en un horario que ya pasó.')
            return redirect(request.path)
        if fecha > limite:
            messages.error(
                request,
                f'La cita debe quedar confirmada antes del {limite} (3 semanas desde que se solicitó).',
            )
            return redirect(request.path)

        cita.fecha = fecha
        cita.hora = hora
        cita.estado = Cita.ESTADO_AGENDADA
        cita.revisada_por = request.user
        cita.revisada_en = timezone.now()
        cita.save(update_fields=['fecha', 'hora', 'estado', 'revisada_por', 'revisada_en'])
        Bitacora.registrar(
            request=request,
            usuario=request.user,
            accion=Bitacora.ACCION_CONFIRMAR_CITA,
            descripcion=(
                f'Confirmó la cita de {cita.paciente} para el {fecha} '
                f'a las {hora_str} (cita #{cita.id}).'
            ),
        )
        messages.success(request, f'Cita de {cita.paciente} confirmada para el {fecha} a las {hora_str}.')
        return redirect(volver_url)

    return render(request, 'pacientes/revisar_solicitud.html', {
        'cita': cita,
        'edad': cita.paciente.edad_en(cita.fecha_sugerida or cita.fecha),
        'limite': limite,
        'volver_url': volver_url,
    })


@login_required
@user_passes_test(es_recepcionista)
def marcar_ausente(request, convenio, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, convenio=convenio)
    if request.method == 'POST':
        if cita.fecha > datetime.date.today():
            messages.error(request, 'No se puede marcar ausente una cita antes de la fecha en que le toca.')
        else:
            cita.estado = Cita.ESTADO_AUSENTE
            cita.save(update_fields=['estado'])
            Bitacora.registrar(
                request=request,
                usuario=request.user,
                accion=Bitacora.ACCION_MARCAR_AUSENTE,
                descripcion=f'Marcó como ausente a {cita.paciente} (cita #{cita.id}).',
            )
            messages.success(request, f'Cita de {cita.paciente} marcada como ausente.')
    return redirect(f'{reverse(f"procesar_citas_{convenio}")}?fecha={cita.fecha}')


@login_required
@user_passes_test(es_recepcionista)
def confirmar_reagenda(request, convenio, cita_id):
    cita = get_object_or_404(Cita, id=cita_id, convenio=convenio)
    calendario_url = reverse(f'calendario_{convenio}')

    if cita.estado != Cita.ESTADO_AUSENTE:
        messages.error(request, 'Solo se pueden reagendar citas marcadas como ausente.')
        return redirect(f'{reverse(f"procesar_citas_{convenio}")}?fecha={cita.fecha}')

    datos = request.POST if request.method == 'POST' else request.GET
    fecha = parse_date(datos.get('fecha', ''))
    hora = datos.get('hora')
    if not fecha or not hora:
        return redirect(f'{calendario_url}?reagendar={cita.id}')

    if request.method == 'POST':
        hora_valor = datetime.datetime.strptime(hora, '%H:%M').time()
        if en_el_pasado(fecha, hora_valor):
            messages.error(request, 'No se pueden reagendar citas a un horario que ya pasó.')
            return redirect(f'{calendario_url}?reagendar={cita.id}')
        if fuera_de_ventana(fecha):
            messages.error(request, 'Solo se pueden reagendar citas hasta 3 semanas después de hoy.')
            return redirect(f'{calendario_url}?reagendar={cita.id}')

        cita.fecha = fecha
        cita.hora = hora_valor
        cita.estado = Cita.ESTADO_AGENDADA
        cita.save(update_fields=['fecha', 'hora', 'estado'])
        Bitacora.registrar(
            request=request,
            usuario=request.user,
            accion=Bitacora.ACCION_REAGENDAR_CITA,
            descripcion=(
                f'Reagendó la cita de {cita.paciente} para el {fecha} '
                f'a las {hora} (cita #{cita.id}).'
            ),
        )
        messages.success(request, f'Cita de {cita.paciente} reagendada para el {fecha} a las {hora}.')
        return redirect(f'{reverse(f"procesar_citas_{convenio}")}?fecha={fecha}')

    return render(request, 'pacientes/reagendar_confirmar.html', {
        'cita': cita,
        'nueva_fecha': fecha,
        'nueva_hora': hora,
        'calendario_url': f'{calendario_url}?reagendar={cita.id}',
    })


# Registrar Ticket: check-in de pacientes que llegan a Emergencia IGSS sin
# cita agendada. Genera un turno numerado (ver Ticket.save) para la fila de
# atención.
@login_required
@user_passes_test(es_recepcionista)
def registrar_ticket_emergencia(request):
    volver_url = reverse('pantalla_placeholder', kwargs={'clave': 'emergencia_igss'})

    if request.method == 'POST':
        form = RegistrarTicketForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            paciente = obtener_o_actualizar_paciente(cd)
            ticket = Ticket.objects.create(
                paciente=paciente,
                servicio=Ticket.SERVICIO_EMERGENCIA_IGSS,
                prioridad=int(cd['prioridad']),
                motivo=cd['motivo'],
                registrado_por=request.user,
            )
            Bitacora.registrar(
                request=request,
                usuario=request.user,
                accion=Bitacora.ACCION_REGISTRAR_TICKET,
                descripcion=(
                    f'Registró el ticket {ticket.turno} de Emergencia IGSS para '
                    f'{paciente.nombre} {paciente.apellido} (DPI {paciente.dpi}).'
                ),
            )
            messages.success(
                request, f'Ticket {ticket.turno} registrado para {paciente.nombre} {paciente.apellido}.'
            )
            return redirect('pantalla_turnos_emergencia')
    else:
        form = RegistrarTicketForm()

    return render(request, 'pacientes/registrar_ticket_emergencia.html', {
        'form': form,
        'volver_url': volver_url,
    })


@login_required
@user_passes_test(es_recepcionista)
def pantalla_turnos_emergencia(request):
    cola = (
        Ticket.objects.filter(servicio=Ticket.SERVICIO_EMERGENCIA_IGSS)
        .exclude(estado__in=[Ticket.ESTADO_ATENDIDO, Ticket.ESTADO_AUSENTE])
        .select_related('paciente')
        .order_by('-prioridad', 'creado_en')
    )
    return render(request, 'pacientes/pantalla_turnos_emergencia.html', {
        'cola': cola,
        'siguiente': cola.first(),
        'volver_url': reverse('pantalla_placeholder', kwargs={'clave': 'emergencia_igss'}),
    })


@login_required
@user_passes_test(es_recepcionista)
def procesar_ticket_emergencia(request, ticket_id):
    """Convierte el ticket en una cita EN_PROCESO + orden de trabajo, lista
    para que el técnico la vea en 'Órdenes pendientes'. Se salta agendado y
    revisión del radiólogo porque el paciente ya está en la clínica."""
    ticket = get_object_or_404(Ticket, id=ticket_id, servicio=Ticket.SERVICIO_EMERGENCIA_IGSS)
    volver_url = reverse('pantalla_turnos_emergencia')

    if ticket.estado != Ticket.ESTADO_EN_ESPERA:
        messages.error(request, f'El ticket {ticket.turno} ya fue procesado.')
        return redirect(volver_url)

    if request.method == 'POST':
        form = ProcesarTicketForm(request.POST)
        if form.is_valid():
            ahora = timezone.localtime()
            cita = Cita.objects.create(
                paciente=ticket.paciente,
                tipo_estudio=form.cleaned_data['tipo_estudio'],
                convenio=Cita.CONVENIO_EMERGENCIA_IGSS,
                estado=Cita.ESTADO_EN_PROCESO,
                fecha=ahora.date(),
                hora=ahora.time(),
                hora_llegada=ticket.creado_en,
                notas=ticket.motivo,
                creada_por=request.user,
            )
            OrdenTrabajo.objects.create(
                cita=cita,
                motivo=form.cleaned_data['motivo'],
                creada_por=request.user,
            )
            ticket.estado = Ticket.ESTADO_ATENDIDO
            ticket.atendido_en = timezone.now()
            ticket.cita = cita
            ticket.save(update_fields=['estado', 'atendido_en', 'cita'])
            _notificar_orden_pendiente(cita)
            Bitacora.registrar(
                request=request,
                usuario=request.user,
                accion=Bitacora.ACCION_PROCESAR_TICKET,
                descripcion=(
                    f'Procesó el ticket {ticket.turno} de Emergencia IGSS y generó la orden de trabajo '
                    f'para {ticket.paciente} (cita #{cita.id}).'
                ),
            )
            messages.success(request, f'Ticket {ticket.turno} procesado: la orden ya está con el técnico.')
            return redirect(volver_url)
    else:
        form = ProcesarTicketForm(initial={'motivo': ticket.motivo})

    return render(request, 'pacientes/procesar_ticket_emergencia.html', {
        'form': form,
        'ticket': ticket,
        'volver_url': volver_url,
    })


MAX_NOTIFICACIONES_EN_CAMPANITA = 20


@login_required
def notificaciones_pendientes(request):
    """Endpoint que la campanita de notificaciones consulta cada cierto
    tiempo (ver includes/notificaciones.html) para saber si hay avisos
    nuevos y hacer sonar el aviso."""
    pendientes = request.user.notificaciones.filter(leida=False)
    notificaciones = list(pendientes[:MAX_NOTIFICACIONES_EN_CAMPANITA])
    return JsonResponse({
        'no_leidas': pendientes.count(),
        'notificaciones': [
            {
                'id': n.id,
                'tipo': n.tipo,
                'mensaje': n.mensaje,
                'url': n.url,
                'creada_en': timezone.localtime(n.creada_en).strftime('%d/%m %H:%M'),
            }
            for n in notificaciones
        ],
    })


@login_required
def marcar_notificacion_leida(request, notificacion_id):
    if request.method == 'POST':
        request.user.notificaciones.filter(id=notificacion_id).update(leida=True)
    return JsonResponse({'ok': True})


@login_required
def marcar_notificaciones_leidas(request):
    if request.method == 'POST':
        request.user.notificaciones.filter(leida=False).update(leida=True)
    return JsonResponse({'ok': True})
