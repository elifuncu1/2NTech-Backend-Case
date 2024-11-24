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
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None and not user.is_superuser:
            login(request, user)
            now = make_aware(datetime.now())  # Mevcut zaman (Django-aware datetime)
            
            tz = pytz.timezone('Europe/Istanbul')

            # Şu anki zamanı al ve yerelleştir
            now = datetime.now()
            now_tz = timezone.now()

            # Başlangıç ve bitiş saatlerini oluştur
            start_time = tz.localize(datetime.combine(now_tz.date(), time(hour=8, minute=0)))
            end_time = tz.localize(datetime.combine(now_tz.date(), time(hour=18, minute=0)))

            # Attendance kaydı (günün ilk girişi kontrolü)
            attendance_today = Attendance.objects.filter(user=user, entry_time=now.date()).first()
            print(f"Bugün için giriş kaydı mevcut mu? {attendance_today is not None}")

            print(now_tz)
            print(start_time)
            if not attendance_today:  # İlk giriş
                if now_tz > start_time:  # Geç kalma durumu
                    late_minutes = (now_tz - start_time).seconds // 60
                    print(f"Kullanıcı {late_minutes} dakika geç kalmış.")
                    user_permission = UserPermission.objects.get(user=request.user)
                    
                    # Yıllık izinden düşme
                    if user_permission.total_leave_minutes > 0:
                        try:
                            total_minutes = user_permission.total_leave_minutes - late_minutes
                            if total_minutes >= 0:
                                user_permission.total_leave_minutes = total_minutes
                                user_permission.save()
                                print(f"Yeni izin dakikaları: {user_permission.total_leave_minutes}")
                            else:
                                messages.error(request, 'Yıllık izin hakkınız dakikalar açısından yetersiz!')
                        except UserPermission.DoesNotExist:
                            messages.error(request, 'İzin bilgileriniz bulunamadı. Lütfen yöneticinize başvurun.')
                    else:
                        messages.error(request, 'Yıllık izin hakkınız kalmamıştır!')

                    # Yetkiliye geç kalma bildirimi gönderme
                    send_late_notification(user_id=user.id, late_minutes=late_minutes)
                    print(f"Yetkiliye {late_minutes} dakika geç kalma bildirimi gönderildi.")

                    messages.warning(
                        request,
                        f'{late_minutes} dakika geç kaldınız. Yıllık izninizden düşülmüştür.'
                    )

                    # **İzin durumu kontrolü - 3 günden az izin kalan kullanıcılar için bildirim gönderme**
                    if user_permission.total_leave_minutes < 4320:  # 4320 dakika = 3 gün
                        send_leave_notification(user_id=user.id)
                        messages.warning(
                            request,
                            'Yıllık izniniz 3 günden az kaldı! Lütfen izin durumunuzu kontrol edin.'
                        )

                    # Attendance kaydı oluştur
                    Attendance.objects.create(
                        user=user,
                        expected_time=late_minutes,
                        entry_time=now_tz
                    )
                    print("Yeni attendance kaydı oluşturuldu.")
                    messages.success(request, 'Giriş başarılı.')
                else:
                    print("Kullanıcı zaten giriş yapmış.")
                    messages.warning(request, 'Zaten giriş yaptınız.')

            print(f"{user.username} giriş yaptı.")
            return redirect('user_dashboard')

        else:
            print("Kullanıcı doğrulanamadı veya süperuser.")
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