"""
URL configuration for workflows app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import WorkflowViewSet, WorkflowExecutionViewSet

router = DefaultRouter()
router.register(r'', WorkflowViewSet, basename='workflow')
router.register(r'executions', WorkflowExecutionViewSet, basename='execution')

urlpatterns = [
    path('', include(router.urls)),
]
