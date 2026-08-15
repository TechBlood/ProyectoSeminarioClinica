from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LoginViewTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='recepcionista1',
            password='testpass123',
            rol=self.user_model.ROL_RECEPCIONISTA,
        )

    # 1. Test de renderizado de la página de inicio de sesión
    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<form')

    # 2. Test de inicio de sesion con credenciales válidas
    def test_login_with_valid_credentials_redirects(self):
        response = self.client.post(
            reverse('login'),
            data={'username': 'recepcionista1', 'password': 'testpass123'},
            follow=True,
        )
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(response.context['user'].is_authenticated)

    # "Para una prueba incorrecta que Jenkins no espera bastaria con cambiar wrongpassword por testpass123
    # para que asi el Jenkins no sepa que hacer ya que no se define eso en la prueba 3"
    # 3. Test de inicio de sesión con credenciales inválidas
    def test_login_with_invalid_credentials_does_not_authenticate(self):
        response = self.client.post(
            reverse('login'),
            data={'username': 'recepcionista1', 'password': 'wrongpassword'},
        )
        self.assertFalse(response.wsgi_request.user.is_authenticated)
