from django.urls import path
from . import views

urlpatterns = [
    path('auth/', views.AuthView.as_view(), name='auth'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('system-info/', views.SystemInfoView.as_view(), name='system-info'),
    path('health/', views.HealthCheckView.as_view(), name='health'),
]
