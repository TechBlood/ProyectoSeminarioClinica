from django.contrib.auth.forms import UserCreationForm

from .models import Usuario


class CrearUsuarioForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'rol')
