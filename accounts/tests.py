from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from accounts.models import Usuario
from pacientes.models import Paciente, TipoEstudio

class PacienteRecepcionTests(TestCase):
    def setUp(self):
        self.recepcionista = Usuario.objects.create_user(
            username='recepcion1',
            password='Password123!',
            rol='recepcionista'
        )
        self.client.login(username='recepcion1', password='Password123!')

        self.tipo_estudio = TipoEstudio.objects.create(
            nombre='Radiografía X',
            precio=150.00,
            activo=True
        )

    def test_registro_paciente_y_cita(self):
        # Siguiente día hábil (Lunes a Viernes)
        fecha_prueba = date.today() + timedelta(days=1)
        while fecha_prueba.weekday() >= 5:
            fecha_prueba += timedelta(days=1)
        
        fecha_str = fecha_prueba.strftime('%Y-%m-%d')
        hora_str = '08:00:00'

        url = f"{reverse('agendar_cita_coex')}?fecha={fecha_str}&hora={hora_str}"
        
        data = {
            'fecha': fecha_str,
            'hora': hora_str,
            'dpi': '1234567890101',
            'nombre': 'Juan',
            'apellido': 'Perez',
            'telefono': '55555555',
            'fecha_nacimiento': '1990-01-01',
            'sexo': 'M',
            'tipo_estudio': self.tipo_estudio.id,
            'notas': 'Sin observaciones',
        }

        response = self.client.post(url, data)
        
        # Si el formulario falla, imprime los errores exactos en la consola de Jenkins
        if 'form' in response.context and response.context['form'].errors:
            print("ERRORES DEL FORMULARIO:", response.context['form'].errors)

        self.assertEqual(response.status_code, 302, "La vista no redirigió, el formulario falló.")
        self.assertTrue(Paciente.objects.filter(dpi='1234567890101').exists())