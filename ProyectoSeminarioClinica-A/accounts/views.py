from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.shortcuts import redirect, render

from .forms import CrearUsuarioForm
from .models import Usuario
from .pantallas import buscar_pantalla, pantallas_de


def es_administrador(user):
    return user.is_authenticated and (user.is_superuser or user.rol == Usuario.ROL_ADMINISTRADOR)


@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html', {'pantallas': pantallas_de(request.user)})


@login_required
def pantalla_placeholder(request, clave):
    pantalla = buscar_pantalla(pantallas_de(request.user), clave)
    if pantalla is None:
        raise Http404
    if pantalla.get('submenu'):
        return render(request, 'accounts/submenu.html', {'pantalla': pantalla})
    return render(request, 'accounts/en_construccion.html', {'pantalla': pantalla})


@login_required
@user_passes_test(es_administrador)
def crear_usuario(request):
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            nuevo_usuario = form.save()
            messages.success(request, f'Usuario "{nuevo_usuario.username}" creado correctamente.')
            return redirect('dashboard')
    else:
        form = CrearUsuarioForm()
    return render(request, 'accounts/crear_usuario.html', {'form': form})
