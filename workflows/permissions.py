"""
Custom permissions for workflow access control.
"""
from rest_framework import permissions


class IsWorkflowOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a workflow to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user owns the workflow.
        
        For Workflow objects, check the user field directly.
        For WorkflowExecution objects, check the workflow's user field.
        """
        # Handle Workflow objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Handle WorkflowExecution objects
        if hasattr(obj, 'workflow'):
            return obj.workflow.user == request.user
        
        return False
