from django.db import models
from django.contrib.auth.models import User

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('beklemede', 'Beklemede'),
        ('onaylandı', 'Onaylandı'),
        ('reddedildi', 'Reddedildi'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    request_date = models.DateTimeField(auto_now_add=True) 
    start_date = models.DateField() 
    end_date = models.DateField() 
    reason = models.TextField(blank=True, null=True)  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='beklemede') 

    class Meta:
        ordering = ['-request_date'] 

    def __str__(self):
        return f"{self.user.username} - {self.start_date} - {self.end_date} ({self.status})"
