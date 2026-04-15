import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

try:
    User = get_user_model()
    if not User.objects.filter(username='KoiEnterprise').exists():
        User.objects.create_superuser('KoiEnterprise', '', 'KoiEnterprise2026')
        print("Superusuario creado con éxito en Neon!")
    else:
        print("El superusuario ya existe.")
except Exception as e:
    print(f"No se pudo crear el superusuario: {e}")
