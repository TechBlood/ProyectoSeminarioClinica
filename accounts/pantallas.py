from .models import Usuario

# Qué botones/pantallas ve cada rol al entrar al sistema. Cada entrada:
# - "nombre": texto del botón
# - "url_name": nombre de una URL real ya implementada (sin parámetros)
# - "clave": si no hay pantalla real todavía, usa esta clave para mostrar
#   un placeholder "en construcción" en /pantalla/<clave>/
# - "submenu": lista de sub-pantallas (mismo formato) que se muestran al
#   entrar a esta pantalla, en vez del placeholder
PANTALLAS_POR_ROL = {
    Usuario.ROL_ADMINISTRADOR: [
        {'nombre': 'Crear usuario', 'url_name': 'crear_usuario'},
    ],
    Usuario.ROL_RECEPCIONISTA: [
        {
            'nombre': 'COEX',
            'clave': 'coex',
            'submenu': [
                {'nombre': 'Agendar cita', 'url_name': 'calendario_coex'},
                {'nombre': 'Procesar cita', 'clave': 'coex_procesar_cita'},
            ],
        },
        {'nombre': 'PRIVADO', 'clave': 'privado'},
        {'nombre': 'EMERGENCIA IGSS', 'clave': 'emergencia_igss'},
    ],
    Usuario.ROL_TECNICO_IMAGENES: [],
    Usuario.ROL_MEDICO_RADIOLOGO: [],
    Usuario.ROL_MEDICO_REMITENTE: [],
}


def pantallas_de(usuario):
    if usuario.is_superuser and usuario.rol != Usuario.ROL_ADMINISTRADOR:
        return PANTALLAS_POR_ROL[Usuario.ROL_ADMINISTRADOR]
    return PANTALLAS_POR_ROL.get(usuario.rol, [])


def buscar_pantalla(pantallas, clave):
    for pantalla in pantallas:
        if pantalla.get('clave') == clave:
            return pantalla
        for hija in pantalla.get('submenu', []):
            if hija.get('clave') == clave:
                return hija
    return None
