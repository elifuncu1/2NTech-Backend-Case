from django.db import models
from django.contrib.auth.models import User

class UserPermission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_leave_minutes = models.IntegerField(default=21600)
