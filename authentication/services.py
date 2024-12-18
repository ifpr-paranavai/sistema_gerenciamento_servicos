import os
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.crypto import get_random_string
from authentication.models import User
from django.conf import settings


class EmailService:
    """Serviço para envio de e-mails."""
    @staticmethod
    def send_reset_password_email(user, token, request):
        # reset_url = request.build_absolute_uri(reverse('reset-password-confirm', kwargs={'token': token}))
        reset_url = f'http://localhost:4200/reset-password?token={token}'
        send_mail(
            subject='Redefinição de Senha',
            message=f'Clique no link para redefinir sua senha: {reset_url}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )


class UserService:
    """Serviço para manipulação de usuários."""
    @staticmethod
    def update_user(user, data):
        user.name = data['name']
        user.email = data['email']
        user.cpf = data['cpf']
        user.profile.profile_picture = data['profile_picture']
        user.profile.street = data['street']
        user.profile.number = data['number']
        user.profile.city = data['city']
        user.profile.state = data['state']
        user.profile.zip_code = data['zip_code']
        
        user.profile.save()
        user.save()
        return user

    @staticmethod
    def generate_reset_password_token(user):
        token = get_random_string(length=32)
        user.password_reset_token = token
        user.save()
        return token
