from django.urls import path
from myapp.views.user_views import user_login, user_logout, user_dashboard
from myapp.views.admin_views import admin_login , staff_dashboard, get_attendance_data, staff_addUser, user_informations, user_edit, user_delete, add_user, monthly_report, get_daily_report
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
def staff_user_add_view(request):
    return add_user(request)

@swagger_auto_schema(method='post', responses={200: openapi.Response('Success')})
@api_view(['POST'])
def staff_user_edit_view(request):
    return user_edit(request)

@swagger_auto_schema(method='post', responses={200: openapi.Response('Success')})
@api_view(['POST'])
def staff_user_delete_view(request):
    return user_delete(request)

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
def staff_dashboard_view(request):
    return staff_dashboard(request)


@swagger_auto_schema(method='get', responses={200: openapi.Response('Success')})
@api_view(['GET'])  
def staff_addUser_view(request):
    return staff_addUser(request)

@swagger_auto_schema(method='get', responses={200: openapi.Response('Success')})
@api_view(['GET'])  
def staff_user_reports_view(request):
    return monthly_report(request)

@swagger_auto_schema(method='get', responses={200: openapi.Response('Success')})
@api_view(['GET'])  
def get_userinformations_view_data(request):
    return user_informations(request)

@swagger_auto_schema(method='get', responses={200: openapi.Response('Success')})
@api_view(['GET'])  
def user_login_view_get(request):
    return user_login(request)

@swagger_auto_schema(method='get', responses={200: openapi.Response('Success')})
@api_view(['GET'])  
def get_attendance_view_data(request):
    return get_attendance_data(request)
urlpatterns = [

    path('', user_login_view_get, name='user_login'),  
    path('attendance-data/', get_attendance_view_data, name='attendance-data'),
    path('user/loginPost/', user_login_post, name='user_login'),  
    path('user/dashboard/', user_dashboard_view, name='user_dashboard'),  
    path('user/logout/', user_logout_view, name='logout'), 
    path('staff/login/', admin_login, name='admin_login'),
    path('staff/daily-report/<int:user_id>/', get_daily_report, name='get_daily_report'),
    path('staff/dashboard/', staff_dashboard_view, name='staff_dashboard'),  
    path('staff/userInformations/', get_userinformations_view_data, name='staff_informations'),  
    path('staff/monthly_report/', staff_user_reports_view, name='monthly_report'),
    path('staff/userReports/', staff_dashboard_view, name='staff_reports'), 
    path('staff/addUser/', staff_addUser_view, name='staff_addUser'), 
    path('staff/addUserPost/', staff_user_add_view, name='add_user_post'), 
    path('staff/user_edit/<int:user_id>/', staff_user_edit_view, name='user_edit'),
    path('staff/user_delete/<int:user_id>/', staff_user_delete_view, name='user_delete'),
    path('staff/leaveRequests/', staff_dashboard_view, name='staff_leaveRequests'), 
]