from django.db import models
from django.contrib.auth.models import User
import json


class Experiment(models.Model):
    """实验模型"""
    EXPERIMENT_TYPES = [
        ('CV', 'Cyclic Voltammetry'),
        ('LSV', 'Linear Sweep Voltammetry'),
        ('SWV', 'Square Wave Voltammetry'),
        ('DPV', 'Differential Pulse Voltammetry'),
        ('NPV', 'Normal Pulse Voltammetry'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experiments')
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    experiment_type = models.CharField(max_length=10, choices=EXPERIMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 实验参数
    start_voltage = models.FloatField(help_text="起始电压 (V)")
    end_voltage = models.FloatField(help_text="结束电压 (V)")
    scan_rate = models.FloatField(help_text="扫描速率 (mV/s)")
    cycles = models.IntegerField(default=1, help_text="循环次数")
    
    # SWV特有参数
    amplitude = models.FloatField(null=True, blank=True, help_text="振幅 (V)")
    frequency = models.FloatField(null=True, blank=True, help_text="频率 (Hz)")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # 标签
    tags = models.JSONField(default=list, blank=True)
    
    # 元数据
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "实验"
        verbose_name_plural = "实验"
    
    def __str__(self):
        return f"{self.name or f'{self.experiment_type} #{self.id}'}"
    
    @property
    def duration(self):
        """计算实验持续时间"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def data_points_count(self):
        """获取数据点数量"""
        return self.data_points.count()


class ExperimentDataPoint(models.Model):
    """实验数据点模型"""
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='data_points')
    timestamp = models.DateTimeField()
    voltage = models.FloatField(help_text="电压 (V)")
    current = models.FloatField(help_text="电流 (A)")
    cycle = models.IntegerField(default=1, help_text="循环次数")
    
    # 额外的测量值
    temperature = models.FloatField(null=True, blank=True, help_text="温度 (°C)")
    ph = models.FloatField(null=True, blank=True, help_text="pH值")
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = "数据点"
        verbose_name_plural = "数据点"
    
    def __str__(self):
        return f"Data point for {self.experiment}"


class Device(models.Model):
    """设备模型"""
    name = models.CharField(max_length=100)
    mac_address = models.CharField(max_length=17, unique=True)
    device_type = models.CharField(max_length=50, default='MSP430')
    firmware_version = models.CharField(max_length=20, blank=True)
    
    # 校准信息
    calibration_date = models.DateTimeField(null=True, blank=True)
    calibration_data = models.JSONField(default=dict, blank=True)
    
    # 设备状态
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "设备"
        verbose_name_plural = "设备"
    
    def __str__(self):
        return f"{self.name} ({self.mac_address})"


class ExperimentTemplate(models.Model):
    """实验模板模型"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='templates')
    experiment_type = models.CharField(max_length=10, choices=Experiment.EXPERIMENT_TYPES)
    
    # 默认参数
    default_parameters = models.JSONField(default=dict)
    
    # 是否公开
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "实验模板"
        verbose_name_plural = "实验模板"
    
    def __str__(self):
        return self.name


class ExperimentResult(models.Model):
    """实验结果模型"""
    experiment = models.OneToOneField(Experiment, on_delete=models.CASCADE, related_name='result')
    
    # 分析结果
    peak_current = models.FloatField(null=True, blank=True, help_text="峰值电流 (A)")
    peak_voltage = models.FloatField(null=True, blank=True, help_text="峰值电压 (V)")
    onset_potential = models.FloatField(null=True, blank=True, help_text="起始电位 (V)")
    
    # 统计信息
    max_current = models.FloatField(null=True, blank=True)
    min_current = models.FloatField(null=True, blank=True)
    avg_current = models.FloatField(null=True, blank=True)
    
    # 分析数据
    analysis_data = models.JSONField(default=dict, blank=True)
    
    # 图表数据
    chart_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "实验结果"
        verbose_name_plural = "实验结果"
    
    def __str__(self):
        return f"Result for {self.experiment}"
