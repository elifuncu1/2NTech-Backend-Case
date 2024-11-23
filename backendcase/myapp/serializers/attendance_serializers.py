# attendance/serializers/attendance_serializers.py
from rest_framework import serializers
from myapp.models.attendanceModel import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'user', 'date', 'check_in_time', 'check_out_time']