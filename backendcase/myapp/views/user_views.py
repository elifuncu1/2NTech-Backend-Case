from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from myapp.models import UserPermission
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and not (user.is_superuser):
            login(request, user)
            return redirect('user_dashboard') 
        else:
            messages.error(request, 'Geçersiz giriş bilgileri veya yetki eksik.')
    return render(request, 'Login/user_login.html')
    
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

    return render(request, 'Dashboard/user_dashboard.html', {'user_info': user_info})


@login_required
def user_logout(request):
    logout(request)
    return redirect('/user/login')