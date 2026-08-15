from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Paciente


class RegistroPacienteTests(TestCase):

    def setUp(self):
        """
        Crea un usuario recepcionista antes de cada prueba
        y lo autentica en el sistema.
        """
        self.user_model = get_user_model()

        self.recepcionista = self.user_model.objects.create_user(
            username='recepcionista_prueba',
            password='testpass123',
            rol=self.user_model.ROL_RECEPCIONISTA,
        )

        self.client.force_login(self.recepcionista)

    def test_registrar_paciente_con_datos_validos(self):
        """
        Verifica que una recepcionista pueda registrar
        correctamente un paciente.
        """
        datos_paciente = {
            'dpi': '1234567890101',
            'nombre': 'Juan',
            'apellido': 'Perez',
            'telefono': '55551234',
            'fecha_nacimiento': '1990-05-20',
            'expediente_igss': 'IGSS-001',
        }

        response = self.client.post(
            reverse('registrar_paciente'),
            data=datos_paciente,
        )

        # Verifica que redirija a buscar pacientes.
        self.assertRedirects(
            response,
            reverse('buscar_paciente'),
            fetch_redirect_response=False,
        )

        # Verifica que se haya creado un solo paciente.
        self.assertEqual(Paciente.objects.count(), 1)

        # Busca al paciente registrado mediante su DPI.
        paciente = Paciente.objects.get(dpi='1234567890101')

        # Verifica que los datos hayan sido guardados.
        self.assertEqual(paciente.nombre, 'Juan')
        self.assertEqual(paciente.apellido, 'Perez')
        self.assertEqual(paciente.telefono, '55551234')
        self.assertEqual(paciente.expediente_igss, 'IGSS-001')

        # Verifica que el expediente interno se haya generado.
        self.assertIsNotNone(paciente.expediente)
        self.assertTrue(paciente.expediente.startswith('CI-'))