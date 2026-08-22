from django.core.mail import EmailMessage


def enviar_resultados(orden):
    paciente = orden.cita.paciente

    if not paciente.correo:
        return

    asunto = f"Resultados de su estudio - CIME"

    mensaje = f"""
Estimado(a) {paciente.nombre} {paciente.apellido}:

Adjunto encontrará los resultados de su estudio realizado en
CIME - Centro de Imágenes Médicas y Especialidades.

Tipo de estudio:
{orden.cita.tipo_estudio.nombre}

Gracias por confiar en nosotros.

Atentamente,

CIME
Centro de Imágenes Médicas y Especialidades
"""

    correo = EmailMessage(
        subject=asunto,
        body=mensaje,
        to=[paciente.correo],
    )

    # Adjuntar informe PDF
    if orden.informe_archivo:
        correo.attach_file(orden.informe_archivo.path)

    # Adjuntar imágenes
    for imagen in orden.imagenes.all():
        correo.attach_file(imagen.archivo.path)

    correo.send()