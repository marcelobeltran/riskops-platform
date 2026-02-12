import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group

def create_analyst():
    username = 'analista1'
    password = 'password123'
    email = 'analista@riskops.com'

    if User.objects.filter(username=username).exists():
        print(f"Usuario '{username}' ya existe. Reseteando password...")
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
    else:
        user = User.objects.create_user(username, email, password)
        print(f"Usuario '{username}' creado.")

    # Assign to Group
    try:
        group = Group.objects.get(name='Risk Analyst')
        user.groups.add(group)
        print(f"Asignado al grupo: Risk Analyst")
    except Group.DoesNotExist:
        print("ERROR: El grupo 'Risk Analyst' no existe. Ejecuta 'python manage.py setup_roles' primero.")
        return

    # Must be staff to access Admin
    user.is_staff = True
    user.save()
    print("Permiso is_staff activado para acceso al Admin.")
    print(f"Credenciales: {username} / {password}")

if __name__ == "__main__":
    create_analyst()
