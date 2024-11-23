# myapp/models/attendance.py
from django.db import models
from django.conf import settings  # settings modülünü içe aktar

class Attendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    check_in_time = models.DateTimeField(null=True, blank=True) 
    check_out_time = models.DateTimeField(null=True, blank=True) 

    def __str__(self):
        return f"{self.user.username} - {self.date}"