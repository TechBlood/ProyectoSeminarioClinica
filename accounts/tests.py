from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class PacienteTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='recepcionista1',
            password='testpass123',
            rol=self.user_model.ROL_RECEPCIONISTA,
        )

    def registro_paciente(self):
        response = self.client.post (reverse('registro_paciente'), data={
            'nombre': 'Pepe Aguilar',
            'cedula': '1234567890',
            'telefono': '0987654321',
            'email': 'pepe@ejemplo.com'
        })
        return response

    def test_registro_paciente(self):
        response = self.registro_paciente()
        self.assertEqual(response.status_code, 200)