"""
Serializers for workflow models.
"""
from rest_framework import serializers
from .models import Workflow, WorkflowExecution, ExecutionLog


class ExecutionLogSerializer(serializers.ModelSerializer):
    """
    Serializer for ExecutionLog model.
    """
    class Meta:
        model = ExecutionLog
        fields = (
            'id',
            'step_name',
            'step_index',
            'status',
            'message',
            'timestamp',
            'duration_seconds'
        )
        read_only_fields = ('id', 'timestamp')


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    """
    Serializer for WorkflowExecution model.
    """
    logs = ExecutionLogSerializer(many=True, read_only=True)
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    
    class Meta:
        model = WorkflowExecution
        fields = (
            'id',
            'workflow',
            'workflow_name',
            'status',
            'current_step',
            'started_at',
            'finished_at',
            'error_message',
            'created_at',
            'task_id',
            'logs'
        )
        read_only_fields = (
            'id',
            'status',
            'current_step',
            'started_at',
            'finished_at',
            'error_message',
            'created_at',
            'task_id'
        )


class WorkflowExecutionListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing executions without logs.
    """
    workflow_name = serializers.CharField(source='workflow.name', read_only=True)
    
    class Meta:
        model = WorkflowExecution
        fields = (
            'id',
            'workflow',
            'workflow_name',
            'status',
            'current_step',
            'started_at',
            'finished_at',
            'created_at',
        )
        read_only_fields = fields


class WorkflowSerializer(serializers.ModelSerializer):
    """
    Serializer for Workflow model.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    executions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Workflow
        fields = (
            'id',
            'user',
            'name',
            'description',
            'steps',
            'created_at',
            'updated_at',
            'executions_count'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_executions_count(self, obj):
        """Get the total number of executions for this workflow."""
        return obj.executions.count()
    
    def validate_steps(self, value):
        """
        Validate that steps is a list of valid step configurations.
        
        Each step must have:
        - type: one of [data_fetch, data_process, ai_inference, notify_user]
        - name: descriptive name for the step
        - config: optional configuration dictionary
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("Steps must be a list")
        
        if len(value) == 0:
            raise serializers.ValidationError("Workflow must have at least one step")
        
        valid_step_types = ['data_fetch', 'data_process', 'ai_inference', 'notify_user']
        
        for idx, step in enumerate(value):
            if not isinstance(step, dict):
                raise serializers.ValidationError(
                    f"Step {idx} must be a dictionary"
                )
            
            if 'type' not in step:
                raise serializers.ValidationError(
                    f"Step {idx} must have a 'type' field"
                )
            
            if step['type'] not in valid_step_types:
                raise serializers.ValidationError(
                    f"Step {idx} has invalid type '{step['type']}'. "
                    f"Must be one of: {', '.join(valid_step_types)}"
                )
            
            if 'name' not in step:
                raise serializers.ValidationError(
                    f"Step {idx} must have a 'name' field"
                )
            
            # Config is optional
            if 'config' in step and not isinstance(step['config'], dict):
                raise serializers.ValidationError(
                    f"Step {idx} config must be a dictionary"
                )
        
        return value


class WorkflowListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing workflows.
    """
    executions_count = serializers.SerializerMethodField()
    steps_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Workflow
        fields = (
            'id',
            'name',
            'description',
            'steps_count',
            'executions_count',
            'created_at',
            'updated_at'
        )
        read_only_fields = fields
    
    def get_executions_count(self, obj):
        """Get the total number of executions for this workflow."""
        return obj.executions.count()
    
    def get_steps_count(self, obj):
        """Get the number of steps in the workflow."""
        return len(obj.steps) if obj.steps else 0
