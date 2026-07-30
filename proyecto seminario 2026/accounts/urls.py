from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from pacientes import views as pacientes_views

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('usuarios/nuevo/', views.crear_usuario, name='crear_usuario'),
    path('pantalla/coex_procesar_cita/', pacientes_views.procesar_cita_coex, name='pantalla_coex_procesar_cita'),
    path('pantalla/<slug:clave>/', views.pantalla_placeholder, name='pantalla_placeholder'),
]
