from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from .utils import create_dynamic_features
        post_migrate.connect(run_after_migrations, sender=self)

def run_after_migrations(sender, **kwargs):
    from .utils import create_dynamic_features
    create_dynamic_features()