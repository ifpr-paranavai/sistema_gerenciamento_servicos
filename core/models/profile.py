from django.db import models
from core.models.mixins import TimeStampedModel

class Profile(TimeStampedModel):

    street = models.CharField(max_length=255)
    number = models.CharField(max_length=6)
    zip_code = models.CharField(max_length=10)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=120)
    profile_picture = models.TextField()
    
    
    def __str__(self):
        return f"{self.street}, {self.number}, {self.zip_code}, {self.city} - {self.state}"
