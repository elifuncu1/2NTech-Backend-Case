from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from myapp.models import UserPermission
from datetime import datetime, timedelta, time
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.timezone import make_aware
from myapp.models.attendanceModel import Attendance 
from myapp.task import send_late_notification, send_leave_notification
import pytz
from myapp.serializers import LeaveRequestForm
from myapp.models import LeaveRequest
from myapp.decorator import user_required
from django.utils.timezone import localtime
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and not user.is_superuser:
            login(request, user)

            now_tz = timezone.now()
            tz = pytz.timezone('Europe/Istanbul')

            start_time = tz.localize(datetime.combine(now_tz.date(), time(hour=8, minute=0)))
            end_time = tz.localize(datetime.combine(now_tz.date(), time(hour=18, minute=0)))
            if now_tz.weekday() in [5, 6]:  
                messages.success(request, 'Hafta sonu giriş başarılı. Log tutulmadı.')
                return redirect('user_dashboard')

            attendance_today = Attendance.objects.filter(user=user, entry_time__date=now_tz.date()).first()

            if not attendance_today:
                if start_time < now_tz < end_time:
                    late_minutes = (now_tz - start_time).seconds // 60

                    try:
                        user_permission = UserPermission.objects.get(user=user)

                        if user_permission.total_leave_minutes >= late_minutes:
                            user_permission.total_leave_minutes -= late_minutes
                            user_permission.save()
                            messages.warning(
                                request,
                                f'{late_minutes} dakika geç kaldınız. Yıllık izninizden düşülmüştür.'
                            )
                        else:
                            messages.error(request, 'Yıllık izin hakkınız yetersiz!')
                    except UserPermission.DoesNotExist:
                        messages.error(request, 'İzin bilgileriniz bulunamadı. Lütfen yöneticinize başvurun.')

                    send_late_notification(user_id=user.id, late_minutes=late_minutes)

                    if user_permission.total_leave_minutes < 4320: 
                        send_leave_notification(user_id=user.id)
                        messages.warning(request, 'Yıllık izniniz 3 günden az kaldı!')

                else: 
                    late_minutes = 0
                    messages.success(request, 'Giriş zamanında yapılmıştır.')

                Attendance.objects.create(
                    user=user,
                    expected_time=late_minutes,
                    entry_time=now_tz
                )
                messages.success(request, 'Giriş başarılı.')
            else:
                messages.warning(request, 'Zaten giriş yaptınız.')

            return redirect('user_dashboard')
        else:
            messages.error(request, 'Geçersiz giriş bilgileri veya yetki eksik.')

    return render(request, 'User/user_login.html')



    
@login_required
@user_required()
def user_dashboard(request):
    user_info = {
        'username': request.user.username,
        'email': request.user.email,
    }
    
    try:
        user_permission = UserPermission.objects.get(user=request.user)
        total_minutes = user_permission.total_leave_minutes  
        days = total_minutes // 1440
        hours = (total_minutes % 1440) // 60 
        minutes = total_minutes % 60
        user_info['total_leave_time'] = f"{days} gün, {hours} saat, {minutes} dakika"
    except UserPermission.DoesNotExist:
        user_info['total_leave_time'] = "0 gün, 0 saat, 0 dakika"
    attendance_data = Attendance.objects.filter(user=request.user).order_by('-entry_time')
    return render(request, 'User/user_dashboard.html', {'user_info': user_info,'attendance_data': attendance_data})

@login_required
@user_required()
def wants_to_leave(request):
    user_info = {
        'username': request.user.username,
        'email': request.user.email,
    }
    
    try:
        user_permission = UserPermission.objects.get(user=request.user)
        total_minutes = user_permission.total_leave_minutes  
        days = total_minutes // 1440
        hours = (total_minutes % 1440) // 60 
        minutes = total_minutes % 60
        user_info['total_leave_time'] = f"{days} gün, {hours} saat, {minutes} dakika"
    except UserPermission.DoesNotExist:
        user_info['total_leave_time'] = "0 gün, 0 saat, 0 dakika"
    return render(request, 'User/user_wants_to_leave.html',{'user_info': user_info})

@login_required
@user_required()
def my_leave_requests(request):
    user_info = {
        'username': request.user.username,
        'email': request.user.email,
    }
    
    try:
        user_permission = UserPermission.objects.get(user=request.user)
        total_minutes = user_permission.total_leave_minutes  
        days = total_minutes // 1440
        hours = (total_minutes % 1440) // 60 
        minutes = total_minutes % 60
        user_info['total_leave_time'] = f"{days} gün, {hours} saat, {minutes} dakika"
    except UserPermission.DoesNotExist:
        user_info['total_leave_time'] = "0 gün, 0 saat, 0 dakika"
    user = request.user
    leave_requests = LeaveRequest.objects.filter(user=user).order_by('-request_date')  
    return render(request, 'User/user_my_leave_requests.html', {'leave_requests': leave_requests,'user_info': user_info})

@login_required
@user_required()
def user_logout(request):
    user = request.user
    now_tz = timezone.now()
    attendance_today = Attendance.objects.filter(user=user, entry_time__date=now_tz.date()).first()
    attendance_today.exit_time = now_tz
    attendance_today.save()

    logout(request)
    return redirect('user_login') 

@login_required
@user_required()
def leave_request_post_view(request):
    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            leave_request.save()
            messages.success(request, "İzin talebiniz başarıyla oluşturuldu.")
            return redirect('/user/my_leave_requests') 
        else:
            messages.error(request, "İzin talebiniz oluşturulurken bir hata oluştu. Lütfen formu kontrol edin.")
    else:
        form = LeaveRequestForm()
    
    return render(request, 'User/my_leave_requests.html', {'form': form})