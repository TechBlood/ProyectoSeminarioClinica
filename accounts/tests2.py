from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from accounts.models import Bitacora, Usuario

UsuarioModel = get_user_model()


def crear_usuario(username='usuario', rol=Usuario.ROL_RECEPCIONISTA, **kwargs):
    return UsuarioModel.objects.create_user(username=username, password='clave-segura-123', rol=rol, **kwargs)


class UsuarioModelTests(TestCase):

    def test_el_rol_por_defecto_es_administrador(self):
        usuario = UsuarioModel.objects.create_user(username='sin_rol', password='clave-segura-123')
        self.assertEqual(usuario.rol, Usuario.ROL_ADMINISTRADOR)

    def test_se_puede_crear_con_un_rol_especifico(self):
        usuario = crear_usuario('tecnico1', rol=Usuario.ROL_TECNICO_IMAGENES)
        self.assertEqual(usuario.rol, Usuario.ROL_TECNICO_IMAGENES)

    def test_los_porcentajes_de_comision_inician_en_cero(self):
        usuario = crear_usuario('radiologo1', rol=Usuario.ROL_MEDICO_RADIOLOGO)
        self.assertEqual(usuario.porcentaje_coex, 0)
        self.assertEqual(usuario.porcentaje_privado, 0)
        self.assertEqual(usuario.porcentaje_emergencia_igss, 0)


class BitacoraModelTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_registrar_guarda_el_usuario_y_la_accion(self):
        usuario = crear_usuario('recepcionista1')

        Bitacora.registrar(accion=Bitacora.ACCION_LOGIN_EXITOSO, usuario=usuario)

        evento = Bitacora.objects.get()
        self.assertEqual(evento.usuario, usuario)
        self.assertEqual(evento.accion, Bitacora.ACCION_LOGIN_EXITOSO)
        self.assertEqual(evento.ip, None)

    def test_registrar_guarda_la_ip_cuando_hay_request(self):
        request = self.factory.post('/login/', REMOTE_ADDR='10.0.0.5')

        Bitacora.registrar(
            accion=Bitacora.ACCION_LOGIN_FALLIDO,
            username_intento='fantasma',
            request=request,
        )

        evento = Bitacora.objects.get()
        self.assertEqual(evento.ip, '10.0.0.5')
        self.assertIsNone(evento.usuario)
        self.assertEqual(evento.username_intento, 'fantasma')

    def test_str_usa_el_username_intento_cuando_no_hay_usuario(self):
        Bitacora.registrar(accion=Bitacora.ACCION_LOGIN_FALLIDO, username_intento='desconocido')
        evento = Bitacora.objects.get()
        self.assertIn('desconocido', str(evento))

    def test_str_usa_el_usuario_cuando_existe(self):
        usuario = crear_usuario('recepcionista2')
        Bitacora.registrar(accion=Bitacora.ACCION_LOGIN_EXITOSO, usuario=usuario)
        evento = Bitacora.objects.get()
        self.assertIn(usuario.username, str(evento))
