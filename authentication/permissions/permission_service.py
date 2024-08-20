from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.backends import BaseBackend
from core.models import User, Feature

class PermissionService:
    @staticmethod
    def has_permission(user: User, feature_name: str) -> bool:
        try:
            feature = Feature.objects.get(name=feature_name)
            return user.role.features.filter(id=feature.id).exists() or user.features.filter(id=feature.id).exists()
        except ObjectDoesNotExist:
            return False

    @staticmethod
    def assign_feature_to_user(user: User, feature_name: str) -> bool:
        try:
            feature = Feature.objects.get(name=feature_name)
            user.features.add(feature)
            return True
        except ObjectDoesNotExist:
            return False

    @staticmethod
    def remove_feature_from_user(user: User, feature_name: str) -> bool:
        try:
            feature = Feature.objects.get(name=feature_name)
            user.features.remove(feature)
            return True
        except ObjectDoesNotExist:
            return False
          
          
class AuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None