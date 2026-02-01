"""
Custom exception handler for consistent API error responses.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the response data
        custom_response_data = {
            'error': True,
            'message': str(exc),
            'status_code': response.status_code,
        }
        
        # Add field-specific errors if available
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response_data['message'] = response.data['detail']
            else:
                custom_response_data['errors'] = response.data
        
        response.data = custom_response_data

    return response
