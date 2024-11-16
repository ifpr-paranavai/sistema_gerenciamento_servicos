from django.core.management.base import BaseCommand

from core.utils.permission_assignment import assign_role_permissions

class Command(BaseCommand):
    help = 'Atribui permissões aos usuários baseado em seus roles'

    def handle(self, *args, **options):
        assign_role_permissions()
        self.stdout.write(
            self.style.SUCCESS('Permissões atribuídas com sucesso!')
        )