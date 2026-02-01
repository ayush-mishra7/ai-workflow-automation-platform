"""
Database models for workflows.
"""
import uuid
from django.db import models
from django.conf import settings


class Workflow(models.Model):
    """
    Workflow model representing an automation workflow.
    
    A workflow consists of multiple ordered steps that are executed sequentially.
    Each step has a type (e.g., data_fetch, data_process, ai_inference, notify_user)
    and configuration parameters.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workflows'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    steps = models.JSONField(
        help_text="List of workflow steps with type and configuration"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workflows'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"


class WorkflowExecution(models.Model):
    """
    WorkflowExecution model tracking the execution state of a workflow.
    
    Tracks the current status, progress, and any errors that occur during execution.
    """
    
    class Status(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        RUNNING = 'RUNNING', 'Running'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='executions'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED
    )
    current_step = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Celery task ID for tracking
    task_id = models.CharField(max_length=255, null=True, blank=True)
    
    class Meta:
        db_table = 'workflow_executions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workflow', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['task_id']),
        ]
    
    def __str__(self):
        return f"{self.workflow.name} - {self.status} - {self.id}"


class ExecutionLog(models.Model):
    """
    ExecutionLog model for step-level logging during workflow execution.
    
    Records detailed information about each step's execution including
    status, timing, and any messages or errors.
    """
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        RUNNING = 'RUNNING', 'Running'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'
        SKIPPED = 'SKIPPED', 'Skipped'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    execution = models.ForeignKey(
        WorkflowExecution,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    step_name = models.CharField(max_length=255)
    step_index = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'execution_logs'
        ordering = ['execution', 'step_index', 'timestamp']
        indexes = [
            models.Index(fields=['execution', 'step_index']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.execution.id} - Step {self.step_index}: {self.step_name} - {self.status}"
