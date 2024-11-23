from django.urls import path
from myapp.views.user_views import user_login, user_logout, user_dashboard
from myapp.views.admin_views import admin_login
from rest_framework.decorators import api_view
from rest_framework import permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Swagger için view'leri tanımlama
@swagger_auto_schema(method='post', responses={200: openapi.Response('Success')})
@api_view(['POST'])
def user_login_post(request):
    return user_login(request)

@swagger_auto_schema(method='post', responses={200: openapi.Response('Success')})
@api_view(['POST']) 
def user_logout_view(request):
    return user_logout(request)

@swagger_auto_schema(method='get', responses={200: openapi.Response('Success')})
@api_view(['GET'])  
def user_dashboard_view(request):
    return user_dashboard(request)

@swagger_auto_schema(method='get', responses={200: openapi.Response('Success')})
@api_view(['GET'])  
def user_login_view_get(request):
    return user_login(request)
urlpatterns = [
    path('user/login/', user_login_view_get, name='user_login'),  
    path('user/loginPost/', user_login_post, name='user_login'),  
    path('user/dashboard/', user_dashboard_view, name='user_dashboard'),  
    path('admin/login/', admin_login, name='admin_login'),
    path('user/logout/', user_logout_view, name='logout'), 
]