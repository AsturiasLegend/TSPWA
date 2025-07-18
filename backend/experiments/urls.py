from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'experiments', views.ExperimentViewSet, basename='experiment')
router.register(r'devices', views.DeviceViewSet)
router.register(r'templates', views.ExperimentTemplateViewSet, basename='template')
router.register(r'results', views.ExperimentResultViewSet, basename='result')

urlpatterns = [
    path('', include(router.urls)),
]
