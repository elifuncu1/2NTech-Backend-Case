# myapp/views/attendance_views.py
from rest_framework import viewsets
from myapp.models.attendanceModel import Attendance
from myapp.serializers.attendance_serializers import AttendanceSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def check_in(self, request):
        attendance, created = Attendance.objects.get_or_create(
            user=request.user,
            date=timezone.now().date()
        )
        attendance.check_in_time = timezone.now()
        attendance.save()
        return Response({'status': 'Checked in', 'check_in_time': attendance.check_in_time})

    @action(detail=False, methods=['post'])
    def check_out(self, request):
        try:
            attendance = Attendance.objects.get(
                user=request.user,
                date=timezone.now().date()
            )
            attendance.check_out_time = timezone.now()
            attendance.save()
            return Response({'status': 'Checked out', 'check_out_time': attendance.check_out_time})
        except Attendance.DoesNotExist:
            return Response({'status': 'No check-in record found for today'}, status=400)
        
 