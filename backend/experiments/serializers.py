from rest_framework import serializers
from .models import Experiment, ExperimentDataPoint, Device, ExperimentTemplate, ExperimentResult


class ExperimentDataPointSerializer(serializers.ModelSerializer):
    """实验数据点序列化器"""
    class Meta:
        model = ExperimentDataPoint
        fields = ['id', 'timestamp', 'voltage', 'current', 'cycle', 'temperature', 'ph']


class ExperimentSerializer(serializers.ModelSerializer):
    """实验序列化器"""
    data_points = ExperimentDataPointSerializer(many=True, read_only=True)
    duration = serializers.ReadOnlyField()
    data_points_count = serializers.ReadOnlyField()
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Experiment
        fields = [
            'id', 'name', 'description', 'experiment_type', 'status',
            'start_voltage', 'end_voltage', 'scan_rate', 'cycles',
            'amplitude', 'frequency', 'tags', 'metadata',
            'created_at', 'updated_at', 'started_at', 'completed_at',
            'duration', 'data_points_count', 'user_name', 'data_points'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'started_at', 'completed_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ExperimentListSerializer(serializers.ModelSerializer):
    """实验列表序列化器（不包含数据点）"""
    duration = serializers.ReadOnlyField()
    data_points_count = serializers.ReadOnlyField()
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Experiment
        fields = [
            'id', 'name', 'description', 'experiment_type', 'status',
            'start_voltage', 'end_voltage', 'scan_rate', 'cycles',
            'amplitude', 'frequency', 'tags',
            'created_at', 'updated_at', 'started_at', 'completed_at',
            'duration', 'data_points_count', 'user_name'
        ]


class DeviceSerializer(serializers.ModelSerializer):
    """设备序列化器"""
    class Meta:
        model = Device
        fields = [
            'id', 'name', 'mac_address', 'device_type', 'firmware_version',
            'calibration_date', 'calibration_data', 'is_active', 'last_seen',
            'created_at', 'updated_at'
        ]


class ExperimentTemplateSerializer(serializers.ModelSerializer):
    """实验模板序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ExperimentTemplate
        fields = [
            'id', 'name', 'description', 'experiment_type',
            'default_parameters', 'is_public', 'user_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ExperimentResultSerializer(serializers.ModelSerializer):
    """实验结果序列化器"""
    experiment_name = serializers.CharField(source='experiment.name', read_only=True)
    
    class Meta:
        model = ExperimentResult
        fields = [
            'id', 'experiment', 'experiment_name',
            'peak_current', 'peak_voltage', 'onset_potential',
            'max_current', 'min_current', 'avg_current',
            'analysis_data', 'chart_data',
            'created_at', 'updated_at'
        ]


class ExperimentCreateSerializer(serializers.ModelSerializer):
    """创建实验序列化器"""
    class Meta:
        model = Experiment
        fields = [
            'name', 'description', 'experiment_type',
            'start_voltage', 'end_voltage', 'scan_rate', 'cycles',
            'amplitude', 'frequency', 'tags', 'metadata'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ExperimentUpdateSerializer(serializers.ModelSerializer):
    """更新实验序列化器"""
    class Meta:
        model = Experiment
        fields = [
            'name', 'description', 'tags', 'metadata', 'status'
        ]


class DataPointBatchSerializer(serializers.Serializer):
    """批量数据点序列化器"""
    experiment_id = serializers.IntegerField()
    data_points = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )
    
    def validate_data_points(self, value):
        """验证数据点格式"""
        required_fields = ['timestamp', 'voltage', 'current']
        for point in value:
            for field in required_fields:
                if field not in point:
                    raise serializers.ValidationError(f"Missing required field: {field}")
        return value
    
    def create(self, validated_data):
        experiment_id = validated_data['experiment_id']
        data_points = validated_data['data_points']
        
        try:
            experiment = Experiment.objects.get(id=experiment_id)
        except Experiment.DoesNotExist:
            raise serializers.ValidationError("Experiment not found")
        
        # 批量创建数据点
        data_point_objects = []
        for point_data in data_points:
            data_point_objects.append(ExperimentDataPoint(
                experiment=experiment,
                timestamp=point_data['timestamp'],
                voltage=point_data['voltage'],
                current=point_data['current'],
                cycle=point_data.get('cycle', 1),
                temperature=point_data.get('temperature'),
                ph=point_data.get('ph')
            ))
        
        ExperimentDataPoint.objects.bulk_create(data_point_objects)
        return {'created_count': len(data_point_objects)}
