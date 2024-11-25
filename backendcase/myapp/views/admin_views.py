from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from myapp.models.attendanceModel import Attendance
from rest_framework.response import Response
from django.utils.timezone import localtime
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from myapp.serializers import UserForm 
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from myapp.decorator import admin_required
from myapp.models import LeaveRequest
from myapp.models import UserPermission
def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        admin = authenticate(request, username=username, password=password)
        if admin is not None and admin.is_superuser:
            login(request, admin)
            return redirect('staff_dashboard')
        else:
            messages.error(request, 'Geçersiz giriş bilgileri veya yetki eksik.')
    return render(request, 'Admin/admin_login.html')

@login_required
@admin_required()
def staff_dashboard(request):
    return render(request, 'Admin/admin_dashboard.html')


@login_required
@admin_required()
def staff_addUser(request):
    return render(request, 'Admin/admin_add_user.html')

@login_required
@admin_required()
def get_attendance_data(request):
    # Sayfa numarası parametresi alıyoruz
    page_number = request.GET.get('page', 1)  # Varsayılan olarak 1. sayfa

    # Verileri alıyoruz
    attendance_data = Attendance.objects.all().values('user__username', 'entry_time', 'expected_time')

    # entry_time'ı istenilen formata dönüştürüyoruz (gün/ay/yıl saat:dakika)
    for data in attendance_data:
        # entry_time'ı dönüştürme
        entry_time = localtime(data['entry_time'])  # Localtime kullanarak zaman dilimi dönüşümü
        data['entry_time'] = entry_time.strftime('%d/%m/%Y %H:%M')  # format: gün/ay/yıl saat:dakika
    
    # Pagination işlemi
    paginator = Paginator(attendance_data, 10)  # Sayfa başına 10 veri gösteriyoruz
    page_obj = paginator.get_page(page_number)

    # Sayfa verisini döndürüyoruz
    return Response({
        'data': list(page_obj),  # Sayfalama işlemiyle elde edilen veriler
        'total_pages': paginator.num_pages,  # Toplam sayfa sayısı
        'current_page': page_obj.number,  # Mevcut sayfa
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,  # Sonraki sayfa numarası
        'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None  # Önceki sayfa numarası
    })

@login_required
@admin_required()
def user_informations(request):
    # is_superuser=False olan kullanıcıları al
    users_list = User.objects.filter(is_superuser=False)
    
    # Sayfalama işlemi
    paginator = Paginator(users_list, 10)  # Sayfa başına 10 kullanıcı
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Template'e gönderilecek veri
    context = {
        'users': page_obj
    }
    return render(request, 'Admin/admin_user_informations.html', context)

@login_required
@admin_required()
def add_user(request):
    if request.method == 'POST':
        # Formdan gelen verileri al
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Kullanıcıyı oluştur
        if username and password and email and first_name and last_name:
            # Kullanıcı adı kontrolü
            if User.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'message': 'Bu kullanıcı adı zaten kullanılıyor. Lütfen başka bir kullanıcı adı seçin.'})
            # E-posta kontrolü
            elif User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Bu e-posta adresi zaten kayıtlı. Lütfen başka bir e-posta adresi kullanın.'})
            else:
                try:
                    # Yeni kullanıcıyı oluştur
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=email,
                        first_name=first_name,
                        last_name=last_name
                    )
                    return JsonResponse({'success': True, 'message': 'Yeni kullanıcı başarıyla eklendi.'})
                except Exception as e:
                    return JsonResponse({'success': False, 'message': f'Bir hata oluştu: {str(e)}'})
        else:
            return JsonResponse({'success': False, 'message': 'Lütfen tüm alanları doldurun.'})

@login_required
@admin_required()
def user_edit(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"{user.username} başarıyla güncellendi.")
            return redirect('user_informations')
    else:
        form = UserForm(instance=user)

    return render(request, 'Admin/admin_user_edit.html', {'form': form, 'user': user})

@login_required
@admin_required()
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, f"{user.username} başarıyla silindi.")
    return redirect('user_informations')

@login_required
@admin_required()
def monthly_report(request):
    now = datetime.now()
    start_date = now.replace(day=1)  # Ayın başı
    end_date = now.replace(month=now.month + 1, day=1)  # Bir sonraki ayın başı

    # Tüm kullanıcıların aylık çalışma saatlerini hesapla
    users_report = []
    users = User.objects.all()  # Tüm kullanıcıları al
    for user in users:
        total_hours = 0  # Başlangıçta 0 saat
        attendance_records = Attendance.objects.filter(
            user=user,
            entry_time__gte=start_date,  # entry_time alanını kullanıyoruz
            entry_time__lt=end_date  # entry_time alanını kullanıyoruz
        )

        # Attendance kayıtlarını kontrol et ve toplam saatleri hesapla
        for record in attendance_records:
            if record.exit_time:  # Eğer çıkış saati varsa
                worked_duration = record.exit_time - record.entry_time
                total_hours += worked_duration.total_seconds() / 3600  # Saat cinsinden

        users_report.append({
            'username': user.username,
            'total_hours': round(total_hours, 2),  # Sonuçları iki ondalıklı rakama yuvarla
            'user_id': user.id
        })

    # Raporu template'e gönder
    return render(request, 'Admin/monthly_report.html', {'users_report': users_report})

@csrf_exempt
@login_required
@admin_required()
def get_daily_report(request, user_id):
    # Verilen user_id'ye ait kullanıcıyı bulalım
    now = datetime.now()
    start_date = now.replace(day=1)
    end_date = now.replace(month=now.month + 1, day=1)

    # Kullanıcıya ait attendance verisini al
    attendance_data = Attendance.objects.filter(
        user_id=user_id, 
        entry_time__gte=start_date,
        entry_time__lt=end_date
    )

    # Rapor verilerini döndür
    report = []
    for attendance in attendance_data:
        report.append({
            'date': attendance.entry_time.date(),
            'entry_time': attendance.entry_time.strftime('%H:%M:%S'),  
            'exit_time': attendance.exit_time.strftime('%H:%M:%S') if attendance.exit_time else 'Çıkış Yok', 
            'worked_hours': attendance.worked_hours,
        })

    return JsonResponse({'report': report})

@admin_required()
def staff_leave_requests(request):
    leave_requests = LeaveRequest.objects.select_related('user').all()  
    user_leave_data = {}

    for leave_request in leave_requests:
        user = leave_request.user
        if user.id not in user_leave_data:
            try:
                user_permission = UserPermission.objects.get(user=user)
                total_minutes = user_permission.total_leave_minutes  
                days = total_minutes // 1440
                hours = (total_minutes % 1440) // 60 
                minutes = total_minutes % 60
                user_leave_data[user.id] = f"{days} gün, {hours} saat, {minutes} dakika"
            except UserPermission.DoesNotExist:
                user_leave_data[user.id] = "0 gün, 0 saat, 0 dakika"

    return render(request, 'Admin/admin_user_leave_requests.html', {
        'leave_requests': leave_requests,
        'user_leave_data': user_leave_data
    })

@admin_required()
def staff_leave_action(request, request_id):
    leave_request = get_object_or_404(LeaveRequest, id=request_id)

    if request.method == "POST":
        action = request.POST.get('action')

        # Eğer izin onaylandıysa
        if action == "approve":
            leave_request.status = "onaylandı"
            try:
                user_permission = UserPermission.objects.get(user=leave_request.user)
                leave_duration = leave_request.end_date - leave_request.start_date
                leave_duration_minutes = leave_duration.total_seconds() // 60 

                if user_permission.total_leave_minutes >= leave_duration_minutes:
                    user_permission.total_leave_minutes -= leave_duration_minutes
                    user_permission.save()
                    messages.success(request, "İzin talebi onaylandı ve kullanıcı izin süresi güncellendi.")
                else:
                    leave_request.status = "beklemede"
                    messages.error(request, "Kullanıcının yeterli izin süresi yok.")
                
            except UserPermission.DoesNotExist:
                messages.error(request, "Kullanıcı izin bilgisi bulunamadı.")
                leave_request.status = "beklemede"  # Durumu tekrar beklemeye al

        elif action == "reject":
            leave_request.status = "reddedildi"
            messages.warning(request, "İzin talebi reddedildi.")
        else:
            messages.error(request, "Geçersiz işlem.")
        
        # İzin talebini kaydet
        leave_request.save()
        return redirect('staff_leaveRequests')

@login_required
@admin_required()
def staff_logout(request):
    logout(request)
    return redirect('admin_login') 