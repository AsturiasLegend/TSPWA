from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import json


class AuthView(APIView):
    """用户认证API"""
    permission_classes = []
    
    def post(self, request):
        action = request.data.get('action')
        
        if action == 'login':
            return self.login(request)
        elif action == 'register':
            return self.register(request)
        elif action == 'logout':
            return self.logout(request)
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
    
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    def register(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        
        if not username or not password:
            return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, password=password, email=email)
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)
    
    def logout(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({'message': 'Logged out successfully'})
        except Token.DoesNotExist:
            return Response({'error': 'Not logged in'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """用户信息API"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined
        })
    
    def put(self, request):
        user = request.user
        data = request.data
        
        # 更新用户信息
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.save()
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        })


class SystemInfoView(APIView):
    """系统信息API"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.conf import settings
        import django
        
        return Response({
            'django_version': django.get_version(),
            'debug': settings.DEBUG,
            'time_zone': settings.TIME_ZONE,
            'language_code': settings.LANGUAGE_CODE,
            'database_engine': settings.DATABASES['default']['ENGINE'],
        })


class HealthCheckView(APIView):
    """健康检查API"""
    permission_classes = []
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'timestamp': json.dumps(request.build_absolute_uri(), default=str),
            'version': '1.0.0'
        })
