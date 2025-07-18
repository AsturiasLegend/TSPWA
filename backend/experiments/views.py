from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from .models import Experiment, ExperimentDataPoint, Device, ExperimentTemplate, ExperimentResult
from .serializers import (
    ExperimentSerializer, ExperimentListSerializer, ExperimentCreateSerializer,
    ExperimentUpdateSerializer, DeviceSerializer, ExperimentTemplateSerializer,
    ExperimentResultSerializer, DataPointBatchSerializer, ExperimentDataPointSerializer
)
import json
from datetime import datetime


class ExperimentViewSet(viewsets.ModelViewSet):
    """实验管理视图集"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Experiment.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExperimentListSerializer
        elif self.action == 'create':
            return ExperimentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ExperimentUpdateSerializer
        return ExperimentSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """开始实验"""
        experiment = self.get_object()
        
        if experiment.status != 'pending':
            return Response({
                'error': 'Experiment must be in pending status to start'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        experiment.status = 'running'
        experiment.started_at = timezone.now()
        experiment.save()
        
        return Response({
            'message': 'Experiment started successfully',
            'experiment': ExperimentSerializer(experiment).data
        })
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """停止实验"""
        experiment = self.get_object()
        
        if experiment.status != 'running':
            return Response({
                'error': 'Experiment must be running to stop'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        experiment.status = 'completed'
        experiment.completed_at = timezone.now()
        experiment.save()
        
        # 生成分析结果
        self._generate_analysis_results(experiment)
        
        return Response({
            'message': 'Experiment stopped successfully',
            'experiment': ExperimentSerializer(experiment).data
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消实验"""
        experiment = self.get_object()
        
        if experiment.status in ['completed', 'cancelled']:
            return Response({
                'error': 'Cannot cancel completed or already cancelled experiment'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        experiment.status = 'cancelled'
        experiment.save()
        
        return Response({
            'message': 'Experiment cancelled successfully',
            'experiment': ExperimentSerializer(experiment).data
        })
    
    @action(detail=True, methods=['post'])
    def add_data_points(self, request, pk=None):
        """添加数据点"""
        experiment = self.get_object()
        
        serializer = DataPointBatchSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response({
                'message': f'Added {result["created_count"]} data points',
                'created_count': result['created_count']
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def data_points(self, request, pk=None):
        """获取实验数据点"""
        experiment = self.get_object()
        data_points = experiment.data_points.all()
        
        # 分页
        page = self.paginate_queryset(data_points)
        if page is not None:
            serializer = ExperimentDataPointSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ExperimentDataPointSerializer(data_points, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """导出实验数据"""
        experiment = self.get_object()
        format_type = request.query_params.get('format', 'json')
        
        if format_type == 'csv':
            return self._export_csv(experiment)
        elif format_type == 'json':
            return self._export_json(experiment)
        else:
            return Response({
                'error': 'Unsupported format. Use "csv" or "json"'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _export_json(self, experiment):
        """导出JSON格式数据"""
        serializer = ExperimentSerializer(experiment)
        return Response(serializer.data)
    
    def _export_csv(self, experiment):
        """导出CSV格式数据"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="experiment_{experiment.id}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'Voltage (V)', 'Current (A)', 'Cycle', 'Temperature (°C)', 'pH'])
        
        for point in experiment.data_points.all():
            writer.writerow([
                point.timestamp.isoformat(),
                point.voltage,
                point.current,
                point.cycle,
                point.temperature or '',
                point.ph or ''
            ])
        
        return response
    
    def _generate_analysis_results(self, experiment):
        """生成分析结果"""
        data_points = experiment.data_points.all()
        
        if not data_points.exists():
            return
        
        # 计算基本统计
        currents = [point.current for point in data_points]
        voltages = [point.voltage for point in data_points]
        
        max_current = max(currents)
        min_current = min(currents)
        avg_current = sum(currents) / len(currents)
        
        # 找到峰值
        peak_index = currents.index(max_current)
        peak_voltage = voltages[peak_index]
        
        # 创建或更新结果
        result, created = ExperimentResult.objects.get_or_create(
            experiment=experiment,
            defaults={
                'peak_current': max_current,
                'peak_voltage': peak_voltage,
                'max_current': max_current,
                'min_current': min_current,
                'avg_current': avg_current,
                'analysis_data': {
                    'total_points': len(currents),
                    'voltage_range': [min(voltages), max(voltages)],
                    'current_range': [min_current, max_current],
                }
            }
        )
        
        if not created:
            result.peak_current = max_current
            result.peak_voltage = peak_voltage
            result.max_current = max_current
            result.min_current = min_current
            result.avg_current = avg_current
            result.save()


class DeviceViewSet(viewsets.ModelViewSet):
    """设备管理视图集"""
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """更新设备状态"""
        device = self.get_object()
        device.last_seen = timezone.now()
        device.is_active = True
        device.save()
        
        return Response({
            'message': 'Device status updated',
            'device': DeviceSerializer(device).data
        })


class ExperimentTemplateViewSet(viewsets.ModelViewSet):
    """实验模板管理视图集"""
    serializer_class = ExperimentTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 返回用户自己的模板和公开的模板
        return ExperimentTemplate.objects.filter(
            Q(user=self.request.user) | Q(is_public=True)
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def create_experiment(self, request, pk=None):
        """从模板创建实验"""
        template = self.get_object()
        
        # 使用模板参数创建实验
        experiment_data = {
            'name': request.data.get('name', f'From template: {template.name}'),
            'description': request.data.get('description', template.description),
            'experiment_type': template.experiment_type,
            **template.default_parameters
        }
        
        serializer = ExperimentCreateSerializer(
            data=experiment_data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            experiment = serializer.save()
            return Response({
                'message': 'Experiment created from template',
                'experiment': ExperimentSerializer(experiment).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExperimentResultViewSet(viewsets.ReadOnlyModelViewSet):
    """实验结果视图集"""
    serializer_class = ExperimentResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ExperimentResult.objects.filter(experiment__user=self.request.user)
