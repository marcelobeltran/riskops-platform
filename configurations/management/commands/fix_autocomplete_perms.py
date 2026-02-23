from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from configurations.models import ConfigListItem

class Command(BaseCommand):
    help = 'Grants view_configlistitem permissions to all staff users to fix autocomplete.'

    def handle(self, *args, **options):
        content_type = ContentType.objects.get_for_model(ConfigListItem)
        permission = Permission.objects.get(
            codename='view_configlistitem',
            content_type=content_type,
        )

        staff_users = User.objects.filter(is_staff=True, is_superuser=False)
        for user in staff_users:
            if not user.has_perm('configurations.view_configlistitem'):
                user.user_permissions.add(permission)
                self.stdout.write(self.style.SUCCESS(f'Permiso concedido a {user.username}'))
            else:
                self.stdout.write(f'Usuario {user.username} ya tiene el permiso.')

        self.stdout.write(self.style.SUCCESS('¡Fix de permisos completado!'))
