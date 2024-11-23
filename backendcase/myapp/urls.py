from django.urls import path
from myapp.views.user_views import user_login, user_logout
from myapp.views.admin_views import admin_login
urlpatterns = [
    path('user/login/', user_login, name='user_login'),
    path('admin/login/', admin_login, name='admin_login'),
    path('logout/', user_logout, name='logout'),
]