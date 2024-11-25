from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from model_bakery import baker
from appointment.models import Appointment
from appointment.models.review import Review
from core.models.feature import Feature
from core.models.role import Role
from service.models import Service
from django.core.files.uploadedfile import SimpleUploadedFile
import json


class AppointmentViewSetTests(APITestCase):

    def setUp(self):
        # Limpar banco de dados antes de configurar os testes
        Appointment.objects.all().delete()
        Service.objects.all().delete()

        self.url = reverse('appointment-list')

        # Criar Features necessárias para operações de agendamentos
        self.features = {
            "list": Feature.objects.get_or_create(name="appointment.list_appointment", defaults={"description": "Pode listar agendamentos"})[0],
            "create": Feature.objects.get_or_create(name="appointment.create_appointment", defaults={"description": "Pode criar agendamentos"})[0],
            "update_status": Feature.objects.get_or_create(name="appointment.update_status_appointment", defaults={"description": "Pode atualizar status de agendamentos"})[0],
        }

        # Criar Role e associar as Features
        self.role = Role.objects.create(name="provider", role_type="provider")
        self.role.features.set(self.features.values())

        # Criar usuário e associar o Role
        self.user = baker.make("authentication.User", role=self.role, is_active=True)
        self.user.save()

        # Autenticar usuário
        self.client.force_authenticate(user=self.user)

        # Criar agendamento inicial para os testes
        self.service = baker.make(Service, duration=60)  # Serviço com duração de 60 minutos
        self.appointment = baker.make(
            Appointment,
            status=Appointment.Status.PENDING,
            appointment_date="2024-12-01T10:00:00Z",
            client=self.user,
            provider=self.user,
        )
        self.appointment.services.add(self.service)

    def test_create_appointment(self):
        # Criar arquivo para simular documento
        document_file = SimpleUploadedFile("Quadro_de_atividades.png", b"dummy_content", content_type="image/png")

        data = {
            "appointment_date": "2024-12-02T10:00:00Z",
            "status": "Agendado",
            "client": str(self.user.id),
            "provider": str(self.user.id),
            "services": [self.service.id],
            "document_requirement_24": document_file,
        }

        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 2)

        # Verificar se o serviço foi associado corretamente ao agendamento
        appointment_services = Appointment.objects.get(id=response.data.get('id')).services.all()
        self.assertIn(self.service, appointment_services)

    def test_create_appointment_with_time_conflict(self):
        document_file = SimpleUploadedFile("Quadro_de_atividades.png", b"dummy_content", content_type="image/png")

        data = {
            "appointment_date": "2024-12-01T10:30:00Z",
            "status": "Agendado",
            "client": str(self.user.id),
            "provider": str(self.user.id),
            "services": [self.service.id],
            "document_requirement_24": document_file,
        }

        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Decodificar o conteúdo da resposta JSON
        response_data = json.loads(response.content)

        # Obter as mensagens de erro relacionadas a "appointment_date"
        error_messages = response_data.get("appointment_date", [])

        # Verificar se "Horário indisponível para agendamento" está em uma das mensagens
        self.assertTrue(
            any("Horário indisponível para agendamento" in message for message in error_messages),
            f"Expected 'Horário indisponível para agendamento' in {error_messages}"
        )

    def test_list_appointments(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_update_status(self):
        url = reverse('appointment-update-status', args=[self.appointment.id])
        data = {"status": "Concluido"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, "Concluido")
        
    def tearDown(self):
        # Limpar banco de dados após cada teste
        Appointment.objects.all().delete()
        Service.objects.all().delete()

class ReviewViewSetTests(APITestCase):

    def setUp(self):
        # URL base para o ViewSet de Review
        self.url = reverse('review-list')

        # Criar Features necessárias para operações de avaliações
        self.features = {
            "list": Feature.objects.get_or_create(name="appointment.list_review", defaults={"description": "Pode listar avaliações"})[0],
            "create": Feature.objects.get_or_create(name="appointment.create_review", defaults={"description": "Pode criar avaliações"})[0],
            "update": Feature.objects.get_or_create(name="appointment.update_review", defaults={"description": "Pode atualizar avaliações"})[0],
            "delete": Feature.objects.get_or_create(name="appointment.destroy_review", defaults={"description": "Pode excluir avaliações"})[0],
        }

        # Criar Role e associar as Features
        self.role = Role.objects.create(name="client", role_type="client")
        self.role.features.set(self.features.values())

        # Criar usuário e associar o Role
        self.user = baker.make("authentication.User", role=self.role, is_active=True)
        self.user.save()

        # Autenticar usuário
        self.client.force_authenticate(user=self.user)

        # Criar agendamento inicial para os testes
        self.appointment = baker.make(
            Appointment,
            status=Appointment.Status.COMPLETED,
            client=self.user,
        )

        # Criar uma avaliação inicial para os testes
        self.review = baker.make(
            Review,
            appointment=self.appointment,
            rating=4,
            comment="Ótimo serviço!"
        )

    def test_list_reviews(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_review(self):
        data = {
            "appointment": str(self.appointment.id),
            "rating": 5,
            "comment": "Excelente serviço!",
            "user": str(self.user.id)
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)

    def test_update_review(self):
        url = reverse('review-detail', args=[self.review.id])
        data = {
            "rating": 3,
            "comment": "Bom, mas pode melhorar.",
            "appointment": str(self.appointment.id),
            "user": str(self.user.id)
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 3)
        self.assertEqual(self.review.comment, "Bom, mas pode melhorar.")

    def test_delete_review(self):
        url = reverse('review-detail', args=[self.review.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def tearDown(self):
        # Limpar banco de dados após cada teste
        Appointment.objects.all().delete()
        Review.objects.all().delete()