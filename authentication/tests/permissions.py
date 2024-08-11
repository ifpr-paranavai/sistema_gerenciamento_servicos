from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from django.contrib.auth import get_user_model
from core.models import Role, Feature
from authentication.models import UserRole

User = get_user_model()

class PermissionTests(TestCase):

    def setUp(self):
        # Criando as permissões e roles usando baker
        self.view_reports_permission = baker.make(Feature, name='pode_ver_relatorios')
        self.edit_users_permission = baker.make(Feature, name='pode_editar_usuarios')
        self.admin_role = baker.make(Role, name='Administrador')
        self.user_role = baker.make(Role, name='Usuário')

        # Associando permissões às roles
        self.admin_role.features.add(self.view_reports_permission, self.edit_users_permission)
        self.user_role.features.add(self.view_reports_permission)

        # Criando usuários com baker
        self.admin_user = baker.make(User)
        self.regular_user = baker.make(User)
        self.no_permission_user = baker.make(User)

        # Associando roles aos usuários
        baker.make(UserRole, user=self.admin_user, role=self.admin_role)
        baker.make(UserRole, user=self.regular_user, role=self.user_role)

    def test_admin_access(self):
        self.client.login(username=self.admin_user.username, password='123456')
        response = self.client.get(reverse('protected_view'), {'required_permission': 'pode_ver_relatorios'})
        self.assertEqual(response.status_code, 200)  # Admin deve ter acesso

    def test_user_access(self):
        self.client.login(username=self.regular_user.username, password='123456')
        response = self.client.get(reverse('protected_view'), {'required_permission': 'pode_ver_relatorios'})
        self.assertEqual(response.status_code, 200)  # Usuário deve ter acesso

    def test_no_permission_access(self):
        self.client.login(username=self.no_permission_user.username, password='123456')
        response = self.client.get(reverse('protected_view'), {'required_permission': 'pode_ver_relatorios'})
        self.assertEqual(response.status_code, 403)  # Usuário sem permissão deve ser negado
