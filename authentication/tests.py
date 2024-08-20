from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from appointment.models import Appointment, Review
from core.models import Feature, Role
from django.urls import reverse

User = get_user_model()

class PermissionTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Criar roles
        self.admin_role = Role.objects.create(name="Admin")
        self.user_role = Role.objects.create(name="User")
        
        # Criar features (permissões)
        self.view_appointment = Feature.objects.create(name="appointment.view_appointment")
        self.add_appointment = Feature.objects.create(name="appointment.add_appointment")
        self.change_appointment = Feature.objects.create(name="appointment.change_appointment")
        self.delete_appointment = Feature.objects.create(name="appointment.delete_appointment")
        
        self.view_review = Feature.objects.create(name="appointment.view_review")
        self.add_review = Feature.objects.create(name="appointment.add_review")
        self.change_review = Feature.objects.create(name="appointment.change_review")
        self.delete_review = Feature.objects.create(name="appointment.delete_review")
        
        # Associar features às roles
        self.admin_role.features.add(
            self.view_appointment, self.add_appointment, 
            self.change_appointment, self.delete_appointment,
            self.view_review, self.add_review, 
            self.change_review, self.delete_review
        )
        self.user_role.features.add(self.view_appointment, self.view_review)
        
        # Criar usuários
        self.admin_user = User.objects.create_user(
            email='admin@test.com', password='adminpass', role=self.admin_role
        )
        self.normal_user = User.objects.create_user(
            email='user@test.com', password='userpass', role=self.user_role
        )
        
        # Criar alguns objetos de teste
        self.appointment = Appointment.objects.create(
            appointment_date='2024-08-21T10:00:00Z',
            status='Scheduled',
            client=self.normal_user,
            provider=self.admin_user
        )
        self.review = Review.objects.create(
            rating=5,
            comment="Great service!",
            service=None  # Você pode precisar criar um objeto Service aqui
        )

    def test_admin_appointment_permissions(self):
        self.client.force_authenticate(user=self.admin_user)
        
        # Test view permission
        response = self.client.get(reverse('appointment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test add permission
        response = self.client.post(reverse('appointment-list'), {
            'appointment_date': '2024-08-22T11:00:00Z',
            'status': 'Scheduled',
            'client': self.normal_user.id,
            'provider': self.admin_user.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test change permission
        response = self.client.patch(reverse('appointment-detail', args=[self.appointment.id]), {
            'status': 'Completed'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test delete permission
        response = self.client.delete(reverse('appointment-detail', args=[self.appointment.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_normal_user_appointment_permissions(self):
        self.client.force_authenticate(user=self.normal_user)
        
        # Test view permission (allowed)
        response = self.client.get(reverse('appointment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test add permission (not allowed)
        response = self.client.post(reverse('appointment-list'), {
            'appointment_date': '2024-08-22T11:00:00Z',
            'status': 'Scheduled',
            'client': self.normal_user.id,
            'provider': self.admin_user.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test change permission (not allowed)
        response = self.client.patch(reverse('appointment-detail', args=[self.appointment.id]), {
            'status': 'Completed'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test delete permission (not allowed)
        response = self.client.delete(reverse('appointment-detail', args=[self.appointment.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_review_permissions(self):
        self.client.force_authenticate(user=self.admin_user)
        
        # Teste similar ao de appointments para reviews
        # ...

    def test_normal_user_review_permissions(self):
        self.client.force_authenticate(user=self.normal_user)
        
        # Teste similar ao de appointments para reviews
        # ...

    def test_unauthenticated_user(self):
        # Test that unauthenticated users can't access any endpoints
        response = self.client.get(reverse('appointment-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.get(reverse('review-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)