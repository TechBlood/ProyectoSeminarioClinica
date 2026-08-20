from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse
from accounts.models import Usuario
from pacientes.models import Paciente, TipoEstudio

class PacienteRecepcionTests(TestCase):
    def setUp(self):
        # 1. Usuario con rol recepcionista
        self.recepcionista = Usuario.objects.create_user(
            username='recepcion1',
            password='Password123!',
            rol='recepcionista'
        )
        self.client.login(username='recepcion1', password='Password123!')

        # 2. Tipo de estudio activo
        self.tipo_estudio = TipoEstudio.objects.create(
            nombre='Radiografía X',
            precio=150.00,
            activo=True
        )

    def test_registro_paciente_y_cita(self):
        # La fecha debe ser mañana para evitar validaciones de fechas pasadas o fuera de ventana
        fecha_valida = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        url = f"{reverse('agendar_cita_coex')}?fecha={fecha_valida}&hora=08:00:00"
        
        data = {
            'fecha': fecha_valida,
            'hora': '08:00:00',
            'dpi': '1234567890101',
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'telefono': '55555555',
            'fecha_nacimiento': '1990-01-01',
            'sexo': 'M',
            'tipo_estudio': self.tipo_estudio.id,
        }

        response = self.client.post(url, data)
        
        # Validar que la petición procesó con éxito
        self.assertIn(response.status_code, [200, 302])
        self.assertTrue(Paciente.objects.filter(dpi='1234567890101').exists())