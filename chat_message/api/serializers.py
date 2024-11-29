from rest_framework import serializers

from authentication.models.user import User

class ChatUserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'profile_picture']

    def get_profile_picture(self, user):
        if user.profile:
            return user.profile.profile_picture
        return None
