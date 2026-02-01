"""
Admin configuration for workflows app.
"""
from django.contrib import admin
from .models import Workflow, WorkflowExecution, ExecutionLog


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    """Admin interface for Workflow model."""
    list_display = ('name', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'user__username', 'user__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'name', 'description')
        }),
        ('Workflow Configuration', {
            'fields': ('steps',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(WorkflowExecution)
class WorkflowExecutionAdmin(admin.ModelAdmin):
    """Admin interface for WorkflowExecution model."""
    list_display = ('id', 'workflow', 'status', 'current_step', 'started_at', 'finished_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'workflow__name', 'task_id')
    readonly_fields = ('id', 'created_at', 'task_id')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Execution Information', {
            'fields': ('id', 'workflow', 'task_id', 'status', 'current_step')
        }),
        ('Timing', {
            'fields': ('started_at', 'finished_at', 'created_at')
        }),
        ('Error Details', {
            'fields': ('error_message',)
        }),
    )


@admin.register(ExecutionLog)
class ExecutionLogAdmin(admin.ModelAdmin):
    """Admin interface for ExecutionLog model."""
    list_display = ('execution', 'step_index', 'step_name', 'status', 'timestamp', 'duration_seconds')
    list_filter = ('status', 'timestamp')
    search_fields = ('execution__id', 'step_name', 'message')
    readonly_fields = ('id', 'timestamp')
    ordering = ('execution', 'step_index', 'timestamp')
    
    fieldsets = (
        ('Log Information', {
            'fields': ('id', 'execution', 'step_index', 'step_name', 'status')
        }),
        ('Details', {
            'fields': ('message', 'duration_seconds', 'timestamp')
        }),
    )
