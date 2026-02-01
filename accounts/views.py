"""
Views for user authentication.
"""
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    LoginSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    
    Creates a new user account and returns user details with JWT tokens.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)
    
    @swagger_auto_schema(
        operation_description="Register a new user account",
        responses={
            201: openapi.Response(
                description="User created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'tokens': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'access': openapi.Schema(type=openapi.TYPE_STRING),
                                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        ),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: "Bad Request - Validation errors"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """
    API endpoint for user login.
    
    Authenticates user credentials and returns JWT tokens.
    """
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)
    
    @swagger_auto_schema(
        operation_description="Login with username and password",
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'tokens': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'access': openapi.Schema(type=openapi.TYPE_STRING),
                                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                            }
                        ),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            401: "Unauthorized - Invalid credentials"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({
                'error': True,
                'message': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
