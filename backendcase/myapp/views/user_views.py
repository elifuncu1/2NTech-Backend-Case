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

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and not user.is_superuser:
            login(request, user)

            # Şu anki zamanı al (time-zone aware)
            now_tz = timezone.now()
            tz = pytz.timezone('Europe/Istanbul')

            # Giriş-çıkış saatleri
            start_time = tz.localize(datetime.combine(now_tz.date(), time(hour=8, minute=0)))
            end_time = tz.localize(datetime.combine(now_tz.date(), time(hour=18, minute=0)))

            # Attendance kaydı (günün ilk girişi kontrolü)
            attendance_today = Attendance.objects.filter(user=user, entry_time__date=now_tz.date()).first()

            if not attendance_today:  # İlk giriş
                if now_tz > end_time:
                    messages.error(request, 'Çalışma saatleri dışında giriş yapılamaz!')
                    return redirect('user_login')

                if now_tz > start_time:  # Geç kalma durumu
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

                    # Yetkiliye bildirim gönderme
                    send_late_notification(user_id=user.id, late_minutes=late_minutes)

                    # İzin azalma bildirimi
                    if user_permission.total_leave_minutes < 4320:  # 4320 dakika = 3 gün
                        send_leave_notification(user_id=user.id)
                        messages.warning(request, 'Yıllık izniniz 3 günden az kaldı!')

                else:  # Zamanında giriş
                    late_minutes = 0
                    messages.success(request, 'Giriş zamanında yapılmıştır.')

                # Attendance kaydı oluştur
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
        print(user_info['total_leave_time'])
    except UserPermission.DoesNotExist:
        user_info['total_leave_time'] = "0 gün, 0 saat, 0 dakika"

    return render(request, 'User/user_dashboard.html', {'user_info': user_info})


@login_required
def user_logout(request):
    now = datetime.now()
    user = request.user
    attendance_today = Attendance.objects.filter(user=user, entry_time__date=now.date()).first()

    if request.method == "POST":
        if not attendance_today:
            # expected_time için bir değer ekliyoruz. Örneğin, giriş zamanına göre bir tahmini saat belirleyebiliriz.
            Attendance.objects.create(user=user, entry_time=now, expected_time=0)  # expected_time'ı da ekledik
        else:
            attendance_today.exit_time = now
            attendance_today.save()

    logout(request)
    return redirect('user_login')  # login sayfasına yönlendirme