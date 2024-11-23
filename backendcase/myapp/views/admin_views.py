from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from myapp.models import Admin 

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        admin = Admin.objects.filter(username=username, password=password).first()
        if admin is not None and admin.is_yetkili:
            login(request, admin)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Geçersiz giriş bilgileri veya yetki eksik.')
    return render(request, 'admin_login.html')