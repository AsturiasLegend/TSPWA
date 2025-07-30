<template>
  <div class="home">
    <el-row :gutter="16" class="responsive-row">
      <!-- 设备状态卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="8">
        <el-card class="status-card">
          <template #header>
            <div class="card-header">
              <span>设备状态</span>
              <el-icon><Connection /></el-icon>
            </div>
          </template>
          <div class="status-content">
            <div class="status-item">
              <span class="label">蓝牙连接:</span>
              <el-tag :type="bluetoothConnected ? 'success' : 'danger'">
                {{ bluetoothConnected ? '已连接' : '未连接' }}
              </el-tag>
            </div>
            <div class="status-item">
              <span class="label">设备名称:</span>
              <span>{{ deviceInfo?.name || '未知设备' }}</span>
            </div>
            <div class="status-item">
              <span class="label">实验状态:</span>
              <el-tag :type="experimentRunning ? 'warning' : 'info'">
                {{ experimentRunning ? '运行中' : '空闲' }}
              </el-tag>
            </div>
            <div class="button-group">
              <el-button 
                :type="bluetoothConnected ? 'danger' : 'primary'"
                @click="toggleConnection"
                :loading="connecting"
                :size="isMobile ? 'small' : 'default'"
                block>
                {{ bluetoothConnected ? '断开连接' : '连接设备' }}
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 快速实验卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="8">
        <el-card class="experiment-card">
          <template #header>
            <div class="card-header">
              <span>快速实验</span>
              <el-icon><DataAnalysis /></el-icon>
            </div>
          </template>
          <div class="experiment-content">
            <div class="experiment-types">
              <el-button 
                v-for="type in experimentTypes"
                :key="type"
                :type="type === selectedType ? 'primary' : 'default'"
                @click="selectExperimentType(type)"
                size="small">
                {{ type }}
              </el-button>
            </div>
            <div class="experiment-actions">
              <el-button 
                type="success"
                :disabled="!bluetoothConnected || experimentRunning"
                @click="startQuickExperiment">
                <el-icon><VideoPlay /></el-icon>
                开始实验
              </el-button>
              <el-button 
                type="danger"
                :disabled="!experimentRunning"
                @click="stopExperiment">
                <el-icon><VideoPause /></el-icon>
                停止实验
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 数据概览卡片 -->
      <el-col :span="8">
        <el-card class="data-card">
          <template #header>
            <div class="card-header">
              <span>数据概览</span>
              <el-icon><Document /></el-icon>
            </div>
          </template>
          <div class="data-content">
            <div class="data-item">
              <span class="label">总实验数:</span>
              <span class="value">{{ totalExperiments }}</span>
            </div>
            <div class="data-item">
              <span class="label">今日实验:</span>
              <span class="value">{{ todayExperiments }}</span>
            </div>
            <div class="data-item">
              <span class="label">最近实验:</span>
              <span class="value">{{ lastExperimentTime }}</span>
            </div>
            <div class="button-group">
              <el-button type="primary" @click="$router.push('/data')">
                查看全部数据
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 实时数据显示 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>实时数据</span>
              <el-icon><TrendCharts /></el-icon>
            </div>
          </template>
          <div v-if="experimentRunning">
            <ElectrochemicalChart 
              :data="realTimeData"
              :type="selectedType"
              :real-time="true"
              :title="`${selectedType} 实时数据`"
              height="300px" />
          </div>
          <div v-else class="no-data">
            <el-empty description="暂无实验数据" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'
import ElectrochemicalChart from '@/components/ElectrochemicalChart.vue'

export default {
  name: 'Home',
  components: {
    ElectrochemicalChart
  },
  data() {
    return {
      connecting: false,
      selectedType: 'CV',
      experimentTypes: ['CV', 'LSV', 'SWV']
    }
  },
  computed: {
    ...mapState('bluetooth', ['bluetoothConnected', 'deviceInfo']),
    ...mapState('experiment', ['isRunning', 'realTimeData']),
    ...mapState('data', ['experiments']),
    ...mapGetters('experiment', ['experimentInProgress', 'currentExperimentData']),
    
    experimentRunning() {
      return this.isRunning || this.experimentInProgress
    },
    
    totalExperiments() {
      return this.experiments.length
    },
    
    todayExperiments() {
      const today = new Date()
      return this.experiments.filter(exp => {
        const expDate = new Date(exp.startTime)
        return expDate.toDateString() === today.toDateString()
      }).length
    },
    
    lastExperimentTime() {
      if (this.experiments.length === 0) return '无'
      const lastExp = this.experiments[0]
      return new Date(lastExp.startTime).toLocaleString()
    }
  },
  
  async mounted() {
    // 初始化蓝牙
    await this.$store.dispatch('bluetooth/initBluetooth')
    
    // 加载实验数据
    await this.$store.dispatch('data/loadExperiments')
  },
  
  methods: {
    async toggleConnection() {
      this.connecting = true
      try {
        if (this.bluetoothConnected) {
          await this.$store.dispatch('bluetooth/disconnect')
        } else {
          await this.$store.dispatch('bluetooth/connect')
        }
      } catch (error) {
        this.$message.error('连接失败: ' + error.message)
      } finally {
        this.connecting = false
      }
    },
    
    selectExperimentType(type) {
      this.selectedType = type
    },
    
    async startQuickExperiment() {
      try {
        // 设置默认参数
        await this.$store.dispatch('experiment/updateParameters', {
          startVoltage: 0,
          endVoltage: 1,
          scanRate: 100,
          cycles: 1
        })
        
        // 设置实验类型
        this.$store.commit('experiment/SET_EXPERIMENT_TYPE', this.selectedType)
        
        // 开始实验
        await this.$store.dispatch('experiment/startExperiment')
        
        this.$message.success('实验已开始')
      } catch (error) {
        this.$message.error('启动实验失败: ' + error.message)
      }
    },
    
    async stopExperiment() {
      try {
        await this.$store.dispatch('experiment/stopExperiment')
        this.$message.success('实验已停止')
      } catch (error) {
        this.$message.error('停止实验失败: ' + error.message)
      }
    }
  }
}
</script>

<style scoped>
.home {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-content, .experiment-content, .data-content {
  padding: 10px 0;
}

.status-item, .data-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.label {
  font-weight: 500;
  color: #666;
}

.value {
  font-weight: 600;
  color: #409EFF;
}

.button-group {
  margin-top: 15px;
  text-align: center;
}

.experiment-types {
  margin-bottom: 15px;
}

.experiment-types .el-button {
  margin-right: 8px;
  margin-bottom: 8px;
}

.experiment-actions {
  display: flex;
  gap: 10px;
}

.no-data {
  text-align: center;
  padding: 40px;
}

.status-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.experiment-card {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.data-card {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}
</style>
