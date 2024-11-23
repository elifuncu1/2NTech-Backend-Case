
from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    is_personel = models.BooleanField(default=False)
    is_yetkili = models.BooleanField(default=False)

    name = models.TextField()
    surname = models.TextField()
    last_login_date = models.DateTimeField() 
