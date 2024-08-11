from django.db import migrations

def create_initial_permissions(apps, schema_editor):
    Feature = apps.get_model('core', 'Feature')
    Role = apps.get_model('core', 'Role')

    # Criando permissões iniciais
    view_reports = Feature.objects.create(name='pode_ver_relatorios', description='Permite visualizar relatórios')
    edit_users = Feature.objects.create(name='pode_editar_usuarios', description='Permite editar usuários')

    # Criando roles iniciais
    admin_role = Role.objects.create(name='Administrador', description='Administrador do sistema')
    user_role = Role.objects.create(name='Usuário', description='Usuário comum')

    # Associando permissões às roles
    admin_role.features.add(view_reports, edit_users)
    user_role.features.add(view_reports)

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_permissions),
    ]
