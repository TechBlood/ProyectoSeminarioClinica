from django.test import TestCase
from django.urls import reverse
from accounts.models import Usuario
from pacientes.models import Paciente, TipoEstudio

class PacienteRecepcionTests(TestCase):
    def setUp(self):
        # 1. Crear un usuario tipo Recepcionista para autenticar la petición
        self.recepcionista = Usuario.objects.create_user(
            username='recepcion1',
            password='Password123!',
            rol='recepcionista' # O el rol que manejes
        )
        self.client.login(username='recepcion1', password='Password123!')

        # 2. Crear un tipo de estudio necesario para agendar la cita
        self.tipo_estudio = TipoEstudio.objects.create(
            nombre='Radiografía X',
            precio=150.00,
            activo=True
        )

    def test_registro_paciente_y_cita(self):
        # Probar el agendamiento (que registra o asocia al paciente)
        url = reverse('agendar_cita_coex')
        
        data = {
            'dpi': '1234567890101',
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'telefono': '55555555',
            'fecha_nacimiento': '1990-01-01',
            'sexo': 'M',
            'tipo_estudio': self.tipo_estudio.id,
            'fecha': '2026-09-01',
            'hora': '08:00:00',
        }

        response = self.client.post(url, data)
        
        # Validar redirección o respuesta exitosa (HTTP 200 o 302)
        self.assertIn(response.status_code, [200, 302])
        
        # Verificar que el paciente realmente se creó en la BD
        self.assertTrue(Paciente.objects.filter(dpi='1234567890101').exists())