from django.db import models

class Admin(models.Model):
    name = models.CharField(max_length=100)
    # Diğer alanlar...