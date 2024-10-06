from django.core.management.base import BaseCommand
from core.utils import create_dynamic_features

class Command(BaseCommand):
    help = 'Cria permissões dinâmicas para todos os modelos'

    def handle(self, *args, **options):
        create_dynamic_features()
        self.stdout.write(self.style.SUCCESS('Permissões dinâmicas criadas com sucesso!'))