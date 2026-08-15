import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinica.settings')
import django
django.setup()
from django.contrib.auth import get_user_model

User = get_user_model()
username = 'admin'
email = 'admin@example.com'
password = 'Admin123!'

u = User.objects.filter(username=username).first()
if not u:
    User.objects.create_superuser(username=username, email=email, password=password)
    print('CREATED')
else:
    u.set_password(password)
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print('UPDATED')
