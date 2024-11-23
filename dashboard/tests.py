# dashboard/tests.py
from datetime import datetime, timedelta
from decimal import Decimal
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from appointment.models.appointment import Appointment
from service.models.service import Service

User = get_user_model()

class DashboardTests(APITestCase):
    def setUp(self):
        # Criar usuário para autenticação
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Criar serviços
        self.service1 = Service.objects.create(
            name='Serviço 1',
            description='Descrição 1',
            value=100.00
        )
        self.service2 = Service.objects.create(
            name='Serviço 2',
            description='Descrição 2',
            value=200.00
        )
        
        # Criar cliente
        self.client_obj = Client.objects.create(
            name='Cliente Teste',
            email='cliente@teste.com'
        )
        
        # Criar appointments
        self.appointment1 = Appointment.objects.create(
            service=self.service1,
            client=self.client_obj,
            date=datetime.now(),
            status='COMPLETED',
            value=100.00
        )
        self.appointment2 = Appointment.objects.create(
            service=self.service2,
            client=self.client_obj,
            date=datetime.now() + timedelta(days=1),
            status='IN_PROGRESS',
            value=200.00
        )

    def test_get_dashboard_stats(self):
        url = reverse('dashboard:dashboard-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['totalRevenue'], '100.00')
        self.assertEqual(len(response.data['serviceStats']), 2)
        self.assertEqual(len(response.data['currentAppointments']), 1)
        self.assertEqual(len(response.data['upcomingAppointments']), 1)

    def test_get_dashboard_stats_with_date_filter(self):
        url = reverse('dashboard:dashboard-stats')
        start_date = datetime.now().isoformat()
        end_date = (datetime.now() + timedelta(days=2)).isoformat()
        
        response = self.client.get(
            f'{url}?startDate={start_date}&endDate={end_date}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['currentAppointments']), 1)

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=None)
        url = reverse('dashboard:dashboard-stats')
        response = self.client.get(url)
        
        self.assertEqual(
            response.status_code, 
            status.HTTP_401_UNAUTHORIZED
        )