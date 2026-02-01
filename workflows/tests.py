"""
Comprehensive tests for workflow functionality.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
import json

from workflows.models import Workflow, WorkflowExecution, ExecutionLog
from workflows.tasks import execute_workflow_task, execute_step

User = get_user_model()


class WorkflowModelTests(TestCase):
    """Tests for Workflow model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_workflow(self):
        """Test creating a workflow."""
        workflow = Workflow.objects.create(
            user=self.user,
            name='Test Workflow',
            description='A test workflow',
            steps=[
                {
                    'type': 'data_fetch',
                    'name': 'Fetch Data',
                    'config': {'source': 'api'}
                }
            ]
        )
        
        self.assertEqual(workflow.name, 'Test Workflow')
        self.assertEqual(workflow.user, self.user)
        self.assertEqual(len(workflow.steps), 1)
        self.assertIsNotNone(workflow.id)
    
    def test_workflow_str(self):
        """Test workflow string representation."""
        workflow = Workflow.objects.create(
            user=self.user,
            name='Test Workflow',
            steps=[]
        )
        
        self.assertEqual(str(workflow), f'Test Workflow - {self.user.username}')


class WorkflowExecutionModelTests(TestCase):
    """Tests for WorkflowExecution model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.workflow = Workflow.objects.create(
            user=self.user,
            name='Test Workflow',
            steps=[{'type': 'data_fetch', 'name': 'Fetch'}]
        )
    
    def test_create_execution(self):
        """Test creating a workflow execution."""
        execution = WorkflowExecution.objects.create(
            workflow=self.workflow,
            status=WorkflowExecution.Status.CREATED
        )
        
        self.assertEqual(execution.status, WorkflowExecution.Status.CREATED)
        self.assertEqual(execution.current_step, 0)
        self.assertIsNone(execution.started_at)
        self.assertIsNone(execution.finished_at)
    
    def test_execution_status_choices(self):
        """Test execution status choices."""
        execution = WorkflowExecution.objects.create(
            workflow=self.workflow
        )
        
        # Test all status transitions
        execution.status = WorkflowExecution.Status.RUNNING
        execution.save()
        self.assertEqual(execution.status, 'RUNNING')
        
        execution.status = WorkflowExecution.Status.SUCCESS
        execution.save()
        self.assertEqual(execution.status, 'SUCCESS')


class WorkflowAPITests(APITestCase):
    """Tests for Workflow API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.workflow_data = {
            'name': 'Test Workflow',
            'description': 'A test workflow',
            'steps': [
                {
                    'type': 'data_fetch',
                    'name': 'Fetch Data',
                    'config': {'source': 'api', 'delay': 1}
                },
                {
                    'type': 'data_process',
                    'name': 'Process Data',
                    'config': {'operation': 'transform', 'delay': 1}
                }
            ]
        }
    
    def test_create_workflow(self):
        """Test creating a workflow via API."""
        response = self.client.post(
            '/api/workflows/',
            data=json.dumps(self.workflow_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Workflow')
        self.assertEqual(len(response.data['steps']), 2)
    
    def test_create_workflow_validation(self):
        """Test workflow validation."""
        # Invalid step type
        invalid_data = self.workflow_data.copy()
        invalid_data['steps'] = [
            {'type': 'invalid_type', 'name': 'Invalid Step'}
        ]
        
        response = self.client.post(
            '/api/workflows/',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_workflows(self):
        """Test listing workflows."""
        Workflow.objects.create(
            user=self.user,
            name='Workflow 1',
            steps=[{'type': 'data_fetch', 'name': 'Fetch'}]
        )
        Workflow.objects.create(
            user=self.user,
            name='Workflow 2',
            steps=[{'type': 'data_process', 'name': 'Process'}]
        )
        
        response = self.client.get('/api/workflows/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_workflow_isolation(self):
        """Test that users can only see their own workflows."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        Workflow.objects.create(
            user=other_user,
            name='Other Workflow',
            steps=[{'type': 'data_fetch', 'name': 'Fetch'}]
        )
        
        response = self.client.get('/api/workflows/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    @patch('workflows.views.execute_workflow_task.delay')
    def test_start_workflow_execution(self, mock_task):
        """Test starting a workflow execution."""
        # Mock Celery task
        mock_task.return_value = MagicMock(id='test-task-id')
        
        workflow = Workflow.objects.create(
            user=self.user,
            name='Test Workflow',
            steps=self.workflow_data['steps']
        )
        
        response = self.client.post(f'/api/workflows/{workflow.id}/start/')
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('execution_id', response.data)
        self.assertIn('task_id', response.data)
        self.assertEqual(response.data['status'], 'CREATED')
        
        # Verify execution was created
        execution = WorkflowExecution.objects.get(id=response.data['execution_id'])
        self.assertEqual(execution.workflow, workflow)
        self.assertEqual(execution.status, WorkflowExecution.Status.CREATED)
    
    def test_get_workflow_status(self):
        """Test getting workflow execution status."""
        workflow = Workflow.objects.create(
            user=self.user,
            name='Test Workflow',
            steps=self.workflow_data['steps']
        )
        
        execution = WorkflowExecution.objects.create(
            workflow=workflow,
            status=WorkflowExecution.Status.RUNNING,
            current_step=1
        )
        
        response = self.client.get(f'/api/workflows/{workflow.id}/status/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'RUNNING')
        self.assertEqual(response.data['current_step'], 1)


class WorkflowTaskTests(TestCase):
    """Tests for Celery workflow tasks."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.workflow = Workflow.objects.create(
            user=self.user,
            name='Test Workflow',
            steps=[
                {
                    'type': 'data_fetch',
                    'name': 'Fetch Data',
                    'config': {'source': 'test', 'delay': 0.1}
                },
                {
                    'type': 'notify_user',
                    'name': 'Notify',
                    'config': {'channel': 'email', 'delay': 0.1}
                }
            ]
        )
    
    def test_execute_step_data_fetch(self):
        """Test executing a data_fetch step."""
        result = execute_step(
            'data_fetch',
            {'source': 'test', 'delay': 0.1},
            'Test Fetch'
        )
        
        self.assertTrue(result['success'])
        self.assertIn('message', result)
    
    def test_execute_step_invalid_type(self):
        """Test executing an invalid step type."""
        with self.assertRaises(ValueError):
            execute_step('invalid_type', {}, 'Invalid Step')
    
    def test_workflow_execution_success(self):
        """Test successful workflow execution."""
        execution = WorkflowExecution.objects.create(
            workflow=self.workflow,
            status=WorkflowExecution.Status.CREATED
        )
        
        # Execute the workflow task
        result = execute_workflow_task(str(execution.id))
        
        # Refresh from database
        execution.refresh_from_db()
        
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(execution.status, WorkflowExecution.Status.SUCCESS)
        self.assertEqual(execution.current_step, 2)
        self.assertIsNotNone(execution.started_at)
        self.assertIsNotNone(execution.finished_at)
        
        # Check logs were created
        logs = ExecutionLog.objects.filter(execution=execution)
        self.assertEqual(logs.count(), 2)
        self.assertTrue(all(log.status == ExecutionLog.Status.SUCCESS for log in logs))
    
    def test_workflow_execution_idempotency(self):
        """Test that completed executions are not re-executed."""
        execution = WorkflowExecution.objects.create(
            workflow=self.workflow,
            status=WorkflowExecution.Status.SUCCESS
        )
        
        result = execute_workflow_task(str(execution.id))
        
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertIn('already completed', result['message'])


class AuthenticationTests(APITestCase):
    """Tests for authentication endpoints."""
    
    def test_user_registration(self):
        """Test user registration."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password_confirm': 'securepass123'
        }
        
        response = self.client.post(
            '/api/auth/register/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_user_login(self):
        """Test user login."""
        # Create user
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
    
    def test_protected_endpoint_without_auth(self):
        """Test accessing protected endpoint without authentication."""
        response = self.client.get('/api/workflows/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
