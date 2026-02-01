"""
URL configuration for AI Workflow Automation Platform.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="AI Workflow Automation Platform API",
        default_version='v1',
        description="""
        A production-ready workflow automation platform with asynchronous task execution.
        
        ## Features
        - JWT-based authentication
        - Create and manage automation workflows
        - Asynchronous workflow execution with Celery
        - Real-time execution tracking and logging
        - Retry logic with exponential backoff
        - Idempotent task handling
        
        ## Authentication
        Use the `/api/auth/register` endpoint to create an account, then `/api/auth/login` 
        to obtain JWT tokens. Include the access token in the Authorization header:
        `Authorization: Bearer <your_access_token>`
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # API endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/workflows/', include('workflows.urls')),
]
