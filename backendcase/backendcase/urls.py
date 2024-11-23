from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Personel ve İzin Takip Sistemi API",
        default_version="v1",
        description="Personel giriş/çıkış saatleri, izin talepleri ve raporlama için API.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="developer@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),  # Swagger'ın public olmasını sağlar
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),  
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),  # JSON dökümantasyonu
]
