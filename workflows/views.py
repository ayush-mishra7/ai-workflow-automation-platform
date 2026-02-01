"""
Views for workflow management and execution.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404

from .models import Workflow, WorkflowExecution, ExecutionLog
from .serializers import (
    WorkflowSerializer,
    WorkflowListSerializer,
    WorkflowExecutionSerializer,
    WorkflowExecutionListSerializer,
    ExecutionLogSerializer
)
from .permissions import IsWorkflowOwner
from .tasks import execute_workflow_task


class WorkflowViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing workflows.
    
    Provides CRUD operations for workflows and custom actions for execution.
    """
    permission_classes = [IsAuthenticated, IsWorkflowOwner]
    
    def get_queryset(self):
        """Return workflows for the current user only."""
        return Workflow.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views."""
        if self.action == 'list':
            return WorkflowListSerializer
        return WorkflowSerializer
    
    @swagger_auto_schema(
        operation_description="Create a new workflow",
        request_body=WorkflowSerializer,
        responses={
            201: WorkflowSerializer,
            400: "Bad Request - Validation errors"
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new workflow."""
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="List all workflows for the authenticated user",
        responses={200: WorkflowListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List all workflows for the current user."""
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Retrieve a specific workflow",
        responses={
            200: WorkflowSerializer,
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific workflow."""
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update a workflow",
        request_body=WorkflowSerializer,
        responses={
            200: WorkflowSerializer,
            400: "Bad Request - Validation errors",
            404: "Not Found"
        }
    )
    def update(self, request, *args, **kwargs):
        """Update a workflow."""
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete a workflow",
        responses={
            204: "No Content - Workflow deleted",
            404: "Not Found"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a workflow."""
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        method='post',
        operation_description="Start workflow execution asynchronously",
        responses={
            202: openapi.Response(
                description="Workflow execution started",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'execution_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            404: "Not Found"
        }
    )
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        Start asynchronous execution of a workflow.
        
        Creates a WorkflowExecution record and dispatches a Celery task.
        """
        workflow = self.get_object()
        
        # Create execution record
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            status=WorkflowExecution.Status.CREATED
        )
        
        # Dispatch Celery task
        task = execute_workflow_task.delay(str(execution.id))
        
        # Update execution with task ID
        execution.task_id = task.id
        execution.save(update_fields=['task_id'])
        
        return Response({
            'execution_id': str(execution.id),
            'task_id': task.id,
            'status': execution.status,
            'message': 'Workflow execution started'
        }, status=status.HTTP_202_ACCEPTED)
    
    @swagger_auto_schema(
        method='get',
        operation_description="Get the latest execution status for a workflow",
        responses={
            200: WorkflowExecutionSerializer,
            404: "Not Found - No executions found"
        }
    )
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """
        Get the latest execution status for a workflow.
        """
        workflow = self.get_object()
        
        # Get the most recent execution
        execution = workflow.executions.order_by('-created_at').first()
        
        if not execution:
            return Response({
                'message': 'No executions found for this workflow'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = WorkflowExecutionSerializer(execution)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        method='get',
        operation_description="List all executions for a workflow",
        responses={200: WorkflowExecutionListSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        """
        List all executions for a workflow.
        """
        workflow = self.get_object()
        executions = workflow.executions.order_by('-created_at')
        
        serializer = WorkflowExecutionListSerializer(executions, many=True)
        return Response(serializer.data)


class WorkflowExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing workflow executions.
    
    Provides read-only access to execution records and logs.
    """
    permission_classes = [IsAuthenticated, IsWorkflowOwner]
    serializer_class = WorkflowExecutionSerializer
    
    def get_queryset(self):
        """Return executions for workflows owned by the current user."""
        return WorkflowExecution.objects.filter(
            workflow__user=self.request.user
        ).select_related('workflow').prefetch_related('logs')
    
    @swagger_auto_schema(
        operation_description="List all workflow executions for the authenticated user",
        responses={200: WorkflowExecutionListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """List all executions for the current user's workflows."""
        queryset = self.get_queryset()
        serializer = WorkflowExecutionListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Retrieve a specific workflow execution with logs",
        responses={
            200: WorkflowExecutionSerializer,
            404: "Not Found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific execution with all logs."""
        return super().retrieve(request, *args, **kwargs)
