from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from experiments.models import Experiment, ExperimentDataPoint
from .models import AnalysisMethod, AnalysisJob, PeakAnalysis, StatisticalAnalysis, ComparisonAnalysis
from .serializers import (
    AnalysisMethodSerializer, AnalysisJobSerializer, PeakAnalysisSerializer,
    StatisticalAnalysisSerializer, ComparisonAnalysisSerializer
)
from .analyzers import (
    PeakDetectionAnalyzer, BaselineCorrectionAnalyzer, SmoothingAnalyzer,
    IntegrationAnalyzer, StatisticalAnalyzer
)
import numpy as np
from celery import shared_task


class AnalysisMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """分析方法视图集"""
    queryset = AnalysisMethod.objects.filter(is_active=True)
    serializer_class = AnalysisMethodSerializer
    permission_classes = [IsAuthenticated]


class AnalysisJobViewSet(viewsets.ModelViewSet):
    """分析任务视图集"""
    serializer_class = AnalysisJobSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AnalysisJob.objects.filter(experiment__user=self.request.user)
    
    def perform_create(self, serializer):
        """创建分析任务"""
        analysis_job = serializer.save()
        
        # 异步执行分析任务
        run_analysis_task.delay(analysis_job.id)
        
        return analysis_job
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """重试分析任务"""
        job = self.get_object()
        
        if job.status != 'failed':
            return Response({
                'error': 'Only failed jobs can be retried'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        job.status = 'pending'
        job.error_message = ''
        job.save()
        
        # 重新执行任务
        run_analysis_task.delay(job.id)
        
        return Response({
            'message': 'Analysis job restarted',
            'job': AnalysisJobSerializer(job).data
        })


class PeakAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """峰值分析视图集"""
    serializer_class = PeakAnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PeakAnalysis.objects.filter(experiment__user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def analyze_experiment(self, request):
        """分析实验的峰值"""
        experiment_id = request.data.get('experiment_id')
        parameters = request.data.get('parameters', {})
        
        try:
            experiment = Experiment.objects.get(id=experiment_id, user=request.user)
        except Experiment.DoesNotExist:
            return Response({
                'error': 'Experiment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 执行峰值分析
        analyzer = PeakDetectionAnalyzer()
        results = analyzer.analyze(experiment, parameters)
        
        # 保存结果
        peak_analyses = []
        for result in results:
            peak_analysis = PeakAnalysis.objects.create(
                experiment=experiment,
                peak_voltage=result['voltage'],
                peak_current=result['current'],
                peak_height=result['height'],
                peak_area=result.get('area', 0),
                peak_width=result.get('width', 0),
                peak_index=result['index'],
                peak_type=result.get('type', 'anodic'),
                confidence=result.get('confidence', 0.0)
            )
            peak_analyses.append(peak_analysis)
        
        serializer = PeakAnalysisSerializer(peak_analyses, many=True)
        return Response({
            'message': f'Found {len(peak_analyses)} peaks',
            'peaks': serializer.data
        })


class StatisticalAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """统计分析视图集"""
    serializer_class = StatisticalAnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return StatisticalAnalysis.objects.filter(experiment__user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def analyze_experiment(self, request):
        """分析实验的统计数据"""
        experiment_id = request.data.get('experiment_id')
        
        try:
            experiment = Experiment.objects.get(id=experiment_id, user=request.user)
        except Experiment.DoesNotExist:
            return Response({
                'error': 'Experiment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 执行统计分析
        analyzer = StatisticalAnalyzer()
        results = analyzer.analyze(experiment)
        
        # 保存结果
        statistical_analysis = StatisticalAnalysis.objects.create(
            experiment=experiment,
            current_mean=results['current_stats']['mean'],
            current_std=results['current_stats']['std'],
            current_min=results['current_stats']['min'],
            current_max=results['current_stats']['max'],
            current_median=results['current_stats']['median'],
            voltage_mean=results['voltage_stats']['mean'],
            voltage_std=results['voltage_stats']['std'],
            voltage_min=results['voltage_stats']['min'],
            voltage_max=results['voltage_stats']['max'],
            voltage_median=results['voltage_stats']['median'],
            data_points_count=results['data_points_count'],
            signal_to_noise_ratio=results.get('snr'),
            analysis_data=results
        )
        
        serializer = StatisticalAnalysisSerializer(statistical_analysis)
        return Response({
            'message': 'Statistical analysis completed',
            'analysis': serializer.data
        })


class ComparisonAnalysisViewSet(viewsets.ModelViewSet):
    """比较分析视图集"""
    serializer_class = ComparisonAnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ComparisonAnalysis.objects.filter(experiments__user=self.request.user).distinct()
    
    @action(detail=True, methods=['post'])
    def run_comparison(self, request, pk=None):
        """运行比较分析"""
        comparison = self.get_object()
        
        experiments = comparison.experiments.all()
        if experiments.count() < 2:
            return Response({
                'error': 'At least 2 experiments are required for comparison'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 执行比较分析
        results = self._perform_comparison(experiments)
        
        # 保存结果
        comparison.comparison_data = results
        comparison.correlation_coefficient = results.get('correlation_coefficient')
        comparison.save()
        
        return Response({
            'message': 'Comparison analysis completed',
            'comparison': ComparisonAnalysisSerializer(comparison).data
        })
    
    def _perform_comparison(self, experiments):
        """执行比较分析"""
        comparison_data = {
            'experiments': [],
            'statistics': {},
            'correlation_matrix': {},
            'peak_comparison': {}
        }
        
        # 收集实验数据
        experiment_data = []
        for exp in experiments:
            data_points = exp.data_points.all()
            voltages = [dp.voltage for dp in data_points]
            currents = [dp.current for dp in data_points]
            
            experiment_data.append({
                'id': exp.id,
                'name': exp.name,
                'type': exp.experiment_type,
                'voltages': voltages,
                'currents': currents,
                'data_points_count': len(voltages)
            })
        
        comparison_data['experiments'] = experiment_data
        
        # 计算相关性（如果有多个实验）
        if len(experiment_data) >= 2:
            # 简单的相关性计算
            exp1_currents = np.array(experiment_data[0]['currents'])
            exp2_currents = np.array(experiment_data[1]['currents'])
            
            # 确保长度一致
            min_len = min(len(exp1_currents), len(exp2_currents))
            exp1_currents = exp1_currents[:min_len]
            exp2_currents = exp2_currents[:min_len]
            
            correlation = np.corrcoef(exp1_currents, exp2_currents)[0, 1]
            comparison_data['correlation_coefficient'] = float(correlation)
        
        return comparison_data


@shared_task
def run_analysis_task(job_id):
    """Celery任务：运行分析"""
    from django.utils import timezone
    
    try:
        job = AnalysisJob.objects.get(id=job_id)
        job.status = 'running'
        job.started_at = timezone.now()
        job.save()
        
        # 获取分析器
        analyzer_map = {
            'peak_detection': PeakDetectionAnalyzer,
            'baseline_correction': BaselineCorrectionAnalyzer,
            'smoothing': SmoothingAnalyzer,
            'integration': IntegrationAnalyzer,
            'statistical_analysis': StatisticalAnalyzer,
        }
        
        analyzer_class = analyzer_map.get(job.method.analysis_type)
        if not analyzer_class:
            raise ValueError(f"Unknown analysis type: {job.method.analysis_type}")
        
        analyzer = analyzer_class()
        results = analyzer.analyze(job.experiment, job.parameters)
        
        # 保存结果
        job.result_data = results
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save()
        
    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        job.save()
        raise e
