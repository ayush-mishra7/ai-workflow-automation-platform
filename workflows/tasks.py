"""
Celery tasks for asynchronous workflow execution.

This module implements the core workflow execution logic with:
- Sequential step execution
- Retry logic with exponential backoff
- Idempotent task handling
- Persistent state updates
- Comprehensive error handling and logging
"""
import time
import logging
from datetime import datetime
from celery import shared_task
from django.utils import timezone
from django.db import transaction

from .models import Workflow, WorkflowExecution, ExecutionLog

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def execute_workflow_task(self, execution_id):
    """
    Main Celery task for executing a workflow.
    
    This task orchestrates the execution of all steps in a workflow,
    handling retries, state persistence, and error recovery.
    
    Args:
        execution_id: UUID of the WorkflowExecution to execute
    
    Returns:
        dict: Execution result with status and message
    """
    try:
        # Fetch the execution object
        execution = WorkflowExecution.objects.select_related('workflow').get(id=execution_id)
        workflow = execution.workflow
        
        logger.info(f"Starting workflow execution: {execution_id}")
        
        # Check if already completed (idempotency)
        if execution.status in [WorkflowExecution.Status.SUCCESS, WorkflowExecution.Status.FAILED]:
            logger.warning(f"Execution {execution_id} already completed with status {execution.status}")
            return {
                'status': execution.status,
                'message': 'Execution already completed',
                'execution_id': str(execution_id)
            }
        
        # Update status to RUNNING if not already
        if execution.status == WorkflowExecution.Status.CREATED:
            execution.status = WorkflowExecution.Status.RUNNING
            execution.started_at = timezone.now()
            execution.task_id = self.request.id
            execution.save(update_fields=['status', 'started_at', 'task_id'])
        
        # Execute each step sequentially
        steps = workflow.steps
        total_steps = len(steps)
        
        for step_index, step in enumerate(steps):
            # Skip already completed steps (for retry scenarios)
            if step_index < execution.current_step:
                logger.info(f"Skipping already completed step {step_index}: {step.get('name')}")
                continue
            
            step_name = step.get('name', f"Step {step_index}")
            step_type = step.get('type')
            step_config = step.get('config', {})
            
            logger.info(f"Executing step {step_index + 1}/{total_steps}: {step_name} ({step_type})")
            
            # Create execution log for this step
            log_entry = ExecutionLog.objects.create(
                execution=execution,
                step_name=step_name,
                step_index=step_index,
                status=ExecutionLog.Status.RUNNING,
                message=f"Starting {step_type} step"
            )
            
            step_start_time = time.time()
            
            try:
                # Execute the step based on its type
                step_result = execute_step(step_type, step_config, step_name)
                
                step_duration = time.time() - step_start_time
                
                # Update log entry with success
                log_entry.status = ExecutionLog.Status.SUCCESS
                log_entry.message = step_result.get('message', 'Step completed successfully')
                log_entry.duration_seconds = step_duration
                log_entry.save()
                
                # Update execution progress
                execution.current_step = step_index + 1
                execution.save(update_fields=['current_step'])
                
                logger.info(f"Step {step_index} completed in {step_duration:.2f}s")
                
            except Exception as step_error:
                step_duration = time.time() - step_start_time
                
                # Update log entry with failure
                log_entry.status = ExecutionLog.Status.FAILED
                log_entry.message = f"Step failed: {str(step_error)}"
                log_entry.duration_seconds = step_duration
                log_entry.save()
                
                logger.error(f"Step {step_index} failed: {str(step_error)}")
                
                # Mark execution as failed
                execution.status = WorkflowExecution.Status.FAILED
                execution.finished_at = timezone.now()
                execution.error_message = f"Failed at step {step_index} ({step_name}): {str(step_error)}"
                execution.save(update_fields=['status', 'finished_at', 'error_message'])
                
                # Retry the entire workflow with exponential backoff
                retry_count = self.request.retries
                if retry_count < self.max_retries:
                    retry_delay = 60 * (2 ** retry_count)  # Exponential backoff: 60s, 120s, 240s
                    logger.info(f"Retrying workflow in {retry_delay}s (attempt {retry_count + 1}/{self.max_retries})")
                    raise self.retry(exc=step_error, countdown=retry_delay)
                else:
                    logger.error(f"Max retries reached for execution {execution_id}")
                    return {
                        'status': 'FAILED',
                        'message': execution.error_message,
                        'execution_id': str(execution_id)
                    }
        
        # All steps completed successfully
        execution.status = WorkflowExecution.Status.SUCCESS
        execution.finished_at = timezone.now()
        execution.save(update_fields=['status', 'finished_at'])
        
        logger.info(f"Workflow execution {execution_id} completed successfully")
        
        return {
            'status': 'SUCCESS',
            'message': 'Workflow completed successfully',
            'execution_id': str(execution_id),
            'total_steps': total_steps
        }
        
    except WorkflowExecution.DoesNotExist:
        logger.error(f"WorkflowExecution {execution_id} not found")
        return {
            'status': 'ERROR',
            'message': 'Execution not found',
            'execution_id': str(execution_id)
        }
    except Exception as e:
        logger.exception(f"Unexpected error in workflow execution {execution_id}")
        
        # Try to update execution status
        try:
            execution = WorkflowExecution.objects.get(id=execution_id)
            execution.status = WorkflowExecution.Status.FAILED
            execution.finished_at = timezone.now()
            execution.error_message = f"Unexpected error: {str(e)}"
            execution.save(update_fields=['status', 'finished_at', 'error_message'])
        except:
            pass
        
        raise


def execute_step(step_type, config, step_name):
    """
    Execute a single workflow step based on its type.
    
    Args:
        step_type: Type of step (data_fetch, data_process, ai_inference, notify_user)
        config: Configuration dictionary for the step
        step_name: Name of the step for logging
    
    Returns:
        dict: Step execution result
    """
    step_handlers = {
        'data_fetch': execute_data_fetch,
        'data_process': execute_data_process,
        'ai_inference': execute_ai_inference,
        'notify_user': execute_notify_user,
    }
    
    handler = step_handlers.get(step_type)
    if not handler:
        raise ValueError(f"Unknown step type: {step_type}")
    
    return handler(config, step_name)


def execute_data_fetch(config, step_name):
    """
    Simulate data fetching step.
    
    In a real implementation, this would fetch data from external sources,
    APIs, databases, etc.
    """
    logger.info(f"[{step_name}] Fetching data with config: {config}")
    
    # Simulate API call or data retrieval
    delay = config.get('delay', 2)
    time.sleep(delay)
    
    source = config.get('source', 'default_source')
    logger.info(f"[{step_name}] Data fetched from {source}")
    
    return {
        'success': True,
        'message': f"Successfully fetched data from {source}",
        'data_size': config.get('expected_records', 100)
    }


def execute_data_process(config, step_name):
    """
    Simulate data processing step.
    
    In a real implementation, this would transform, clean, or aggregate data.
    """
    logger.info(f"[{step_name}] Processing data with config: {config}")
    
    # Simulate data processing
    delay = config.get('delay', 3)
    time.sleep(delay)
    
    operation = config.get('operation', 'transform')
    logger.info(f"[{step_name}] Data processed using {operation}")
    
    return {
        'success': True,
        'message': f"Successfully processed data using {operation}",
        'records_processed': config.get('records', 100)
    }


def execute_ai_inference(config, step_name):
    """
    Simulate AI inference step.
    
    In a real implementation, this would call ML models, LLMs, or AI services.
    """
    logger.info(f"[{step_name}] Running AI inference with config: {config}")
    
    # Simulate AI model inference
    delay = config.get('delay', 5)
    time.sleep(delay)
    
    model = config.get('model', 'default_model')
    logger.info(f"[{step_name}] AI inference completed using {model}")
    
    return {
        'success': True,
        'message': f"Successfully ran inference using {model}",
        'confidence': 0.95,
        'predictions': config.get('expected_predictions', 10)
    }


def execute_notify_user(config, step_name):
    """
    Simulate user notification step.
    
    In a real implementation, this would send emails, SMS, push notifications, etc.
    """
    logger.info(f"[{step_name}] Sending notification with config: {config}")
    
    # Simulate notification sending
    delay = config.get('delay', 1)
    time.sleep(delay)
    
    channel = config.get('channel', 'email')
    recipient = config.get('recipient', 'user@example.com')
    logger.info(f"[{step_name}] Notification sent via {channel} to {recipient}")
    
    return {
        'success': True,
        'message': f"Successfully sent notification via {channel} to {recipient}",
        'channel': channel
    }
