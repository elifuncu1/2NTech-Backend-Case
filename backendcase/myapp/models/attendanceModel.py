from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry_time = models.DateTimeField()
    exit_time = models.DateTimeField(null=True, blank=True)
    worked_hours = models.FloatField(default=0)
    expected_time = models.IntegerField(null=True, blank=True, default=0)
    def save(self, *args, **kwargs):
        if self.entry_time and self.exit_time:
            time_diff = self.exit_time - self.entry_time
            self.worked_hours = time_diff.total_seconds() / 3600
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.worked_hours} hours"