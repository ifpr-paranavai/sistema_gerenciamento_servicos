from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient
from core.models.feature import Feature
from core.models.role import Role
from authentication.models import User


class DynamicPermissionTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('document-list')

        self.feature, _ = Feature.objects.get_or_create(
            name='documents.list_document',
            defaults={'description': 'Permissão para listar documentos'}
        )

        self.role = baker.make(Role, role_type='provider')
        self.role.features.add(self.feature)

        self.user = baker.make(User, role=self.role)
        self.client.force_authenticate(user=self.user)

    def test_user_has_permission(self):

        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Usuário com permissão não conseguiu acessar a URL"
        )

    def test_user_has_no_permission(self):

        self.role.features.clear()
        response = self.client.get(self.url)
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Usuário sem permissão conseguiu acessar a URL"
        )
