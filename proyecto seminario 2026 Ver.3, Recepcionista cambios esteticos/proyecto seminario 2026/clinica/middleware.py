from django.utils.deprecation import MiddlewareMixin


class NoCacheMiddleware(MiddlewareMixin):
    """Añade cabeceras para evitar caching en páginas sensibles y prevenir volver atrás tras logout.

    En entornos donde el navegador guarda páginas en el bfcache, estas cabeceras junto con una comprobación
    del estado de sesión en el cliente deberían forzar una recarga.
    """

    def process_response(self, request, response):
        # Solo añadir en respuestas HTML para no interferir con assets estáticos
        content_type = response.get('Content-Type', '')
        if 'text/html' in content_type:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response
