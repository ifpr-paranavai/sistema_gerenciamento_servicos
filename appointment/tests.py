from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from model_bakery import baker
from appointment.api.views import AppointmentViewSet, ReviewViewSet
from authentication.models.user import User
from service.models.service import Service

class PermissionTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client_user = baker.make(User, email="client@example.com", _fill_optional=True)
        self.provider_user = baker.make(User, email="provider@example.com", _fill_optional=True)
        self.service = baker.make(Service, _fill_optional=True)
        self.user = baker.make(User, email="test@example.com", _fill_optional=True)
        self.role = baker.make('core.Role', name='admin')
        self.role.features.add(
            baker.make('core.Feature', name="appointment.view_appointment"),
            baker.make('core.Feature', name="appointment.add_appointment")
        )
        self.user.role = self.role
        self.user.save()

    def test_has_permission_add(self):
        appointment_data = {
            'appointment_date': timezone.now() + timezone.timedelta(days=1),
            'status': 'scheduled',
            'client': self.client_user.id,
            'provider': self.provider_user.id,
            'services': [self.service.id],
            'is_completed': False
        }
        request = self.factory.post('/appointments/', appointment_data, format='json')
        view = AppointmentViewSet.as_view({'post': 'create'})
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, 201)

    def test_no_permission(self):
        request = self.factory.get('/reviews/')
        view = ReviewViewSet.as_view({'get': 'list'})
        force_authenticate(request, user=baker.make(User, is_active=False))
        response = view(request)
        self.assertEqual(response.status_code, 403)
