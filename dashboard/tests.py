# dashboard/tests.py
from datetime import datetime, timedelta
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from unittest.mock import patch, MagicMock

from core.models.role import Role
from core.models.feature import Feature
from appointment.models.appointment import Appointment
from service.models.service import Service
from authentication.models import User

class DashboardTests(APITestCase):
    def setUp(self):
        # Criar role
        self.role = Role.objects.create(role_type='provider')
        
        # Criar usuário
        self.user = User.objects.create(
            email='testuser@test.com',
            name='Test User',
            password='testpass123',
            cpf='12345678901'
        )
        self.user.role = self.role
        self.user.save()

        # Adicionar feature
        self.feature = Feature.objects.create(
            name='dashboard.view_stats',
            description='Can view dashboard stats'
        )
        self.user.features.add(self.feature)
        
        # Mock has_permission method
        self.user.has_permission = MagicMock(return_value=True)
        
        self.client.force_authenticate(user=self.user)
        
        # Criar serviços
        self.service1 = Service.objects.create(
            name='Serviço 1',
            description='Descrição 1',
            cost=Decimal('100.00'),
            duration=30
        )
        self.service2 = Service.objects.create(
            name='Serviço 2',
            description='Descrição 2',
            cost=Decimal('200.00'),
            duration=60
        )
        
        # Criar appointments com timezone aware
        current_time = timezone.now()
        self.appointment1 = Appointment.objects.create(
            client=self.user,
            provider=self.user,
            appointment_date=current_time,
            status=Appointment.Status.COMPLETED
        )
        self.appointment1.services.add(self.service1)

        self.appointment2 = Appointment.objects.create(
            client=self.user,
            provider=self.user,
            appointment_date=current_time + timedelta(days=1),
            status=Appointment.Status.IN_PROGRESS
        )
        self.appointment2.services.add(self.service2)

    @patch('core.models.mixins.DynamicViewPermissions.has_permission')
    def test_get_dashboard_stats(self, mock_has_permission):
        mock_has_permission.return_value = True
        url = reverse('dashboard-stats-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('serviceStats', response.data)
        self.assertIn('currentAppointments', response.data)
        self.assertIn('upcomingAppointments', response.data)

    @patch('core.models.mixins.DynamicViewPermissions.has_permission')
    def test_get_dashboard_stats_with_date_filter(self, mock_has_permission):
        mock_has_permission.return_value = True
        url = reverse('dashboard-stats-list')
        
        # Formatar as datas usando timezone
        start_date = timezone.now().date().isoformat()
        end_date = (timezone.now() + timedelta(days=2)).date().isoformat()
        
        response = self.client.get(
            url,
            {'startDate': start_date, 'endDate': end_date}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('core.models.mixins.DynamicViewPermissions.has_permission')
    def test_unauthorized_access(self, mock_has_permission):
        mock_has_permission.return_value = False
        self.client.force_authenticate(user=None)
        url = reverse('dashboard-stats-list')
        response = self.client.get(url)
        
        self.assertEqual(
            response.status_code, 
            status.HTTP_403_FORBIDDEN
        )