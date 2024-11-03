from django.apps import apps as django_apps
from django.db import IntegrityError

FIXED_FEATURES = [
    ('clients_userviewset', 'Listar clientes do sistema'),
    ('providers_userviewset', 'Listar prestadores do sistema'),
    ('documents.download_document', 'Realizar download de documentos'),
    ('documents.preview_document', 'Visualizar preview de documentos'),
]

def create_dynamic_features(apps=None):
    if apps is None:
        apps = django_apps

    Feature = apps.get_model('core', 'Feature')  # Ajuste 'core' para o app correto onde Feature está definido

    for model in apps.get_models():
        if model._meta.app_label in ['admin', 'contenttypes', 'sessions', 'auth']:
            continue  # Pular modelos internos do Django

        app_label = model._meta.app_label
        model_name = model._meta.model_name

        for action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            name = f'{app_label}.{action}_{model_name}'
            description = f'Can {action} {model_name} in {app_label}'

            try:
                Feature.objects.get_or_create(
                    name=name,
                    defaults={'description': description}
                )
            except IntegrityError:
                # A feature já existe, então vamos apenas atualizá-la
                feature = Feature.objects.get(name=name)
                feature.description = description
                feature.save()

    for name, description in FIXED_FEATURES:
        try:
            Feature.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
        except IntegrityError:
            feature = Feature.objects.get(name=name)
            feature.description = description
            feature.save()

    print("Features dinâmicas criadas ou atualizadas com sucesso!")