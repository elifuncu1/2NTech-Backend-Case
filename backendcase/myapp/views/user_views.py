from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_personel:
            login(request, user)
            return redirect('personel_dashboard') 
        else:
            messages.error(request, 'Geçersiz giriş bilgileri veya yetki eksik.')
    return render(request, 'Login/user_login.html')
    
def user_logout(request):
    logout(request)
    return redirect('home')