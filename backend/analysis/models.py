from django.db import models
from experiments.models import Experiment, ExperimentResult


class AnalysisMethod(models.Model):
    """分析方法模型"""
    ANALYSIS_TYPES = [
        ('peak_detection', '峰值检测'),
        ('baseline_correction', '基线校正'),
        ('smoothing', '平滑滤波'),
        ('integration', '积分计算'),
        ('derivative', '导数计算'),
        ('fourier_transform', '傅里叶变换'),
        ('statistical_analysis', '统计分析'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    analysis_type = models.CharField(max_length=50, choices=ANALYSIS_TYPES)
    parameters = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "分析方法"
        verbose_name_plural = "分析方法"
    
    def __str__(self):
        return self.name


class AnalysisJob(models.Model):
    """分析任务模型"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='analysis_jobs')
    method = models.ForeignKey(AnalysisMethod, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    parameters = models.JSONField(default=dict, blank=True)
    
    # 结果数据
    result_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "分析任务"
        verbose_name_plural = "分析任务"
    
    def __str__(self):
        return f"{self.method.name} for {self.experiment}"


class PeakAnalysis(models.Model):
    """峰值分析结果模型"""
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='peak_analyses')
    
    # 峰值信息
    peak_voltage = models.FloatField(help_text="峰值电压 (V)")
    peak_current = models.FloatField(help_text="峰值电流 (A)")
    peak_height = models.FloatField(help_text="峰值高度")
    peak_area = models.FloatField(help_text="峰面积")
    peak_width = models.FloatField(help_text="峰宽")
    
    # 峰值位置
    peak_index = models.IntegerField(help_text="峰值在数据中的索引")
    
    # 峰值分类
    peak_type = models.CharField(max_length=20, choices=[
        ('anodic', '阳极峰'),
        ('cathodic', '阴极峰'),
        ('mixed', '混合峰'),
    ], default='anodic')
    
    # 置信度
    confidence = models.FloatField(default=0.0, help_text="置信度 (0-1)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "峰值分析"
        verbose_name_plural = "峰值分析"
    
    def __str__(self):
        return f"Peak at {self.peak_voltage}V for {self.experiment}"


class StatisticalAnalysis(models.Model):
    """统计分析结果模型"""
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='statistical_analyses')
    
    # 电流统计
    current_mean = models.FloatField(help_text="电流均值")
    current_std = models.FloatField(help_text="电流标准差")
    current_min = models.FloatField(help_text="电流最小值")
    current_max = models.FloatField(help_text="电流最大值")
    current_median = models.FloatField(help_text="电流中位数")
    
    # 电压统计
    voltage_mean = models.FloatField(help_text="电压均值")
    voltage_std = models.FloatField(help_text="电压标准差")
    voltage_min = models.FloatField(help_text="电压最小值")
    voltage_max = models.FloatField(help_text="电压最大值")
    voltage_median = models.FloatField(help_text="电压中位数")
    
    # 其他统计量
    data_points_count = models.IntegerField(help_text="数据点总数")
    signal_to_noise_ratio = models.FloatField(null=True, blank=True, help_text="信噪比")
    
    # 详细分析结果
    analysis_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "统计分析"
        verbose_name_plural = "统计分析"
    
    def __str__(self):
        return f"Statistical analysis for {self.experiment}"


class ComparisonAnalysis(models.Model):
    """比较分析模型"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    experiments = models.ManyToManyField(Experiment, related_name='comparisons')
    
    # 比较结果
    comparison_data = models.JSONField(default=dict, blank=True)
    
    # 相关性分析
    correlation_coefficient = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "比较分析"
        verbose_name_plural = "比较分析"
    
    def __str__(self):
        return self.name
