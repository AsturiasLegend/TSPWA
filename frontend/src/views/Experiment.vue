<template>
  <div class="experiment">
    <el-row :gutter="20">
      <!-- 实验参数设置 -->
      <el-col :span="8">
        <el-card class="parameter-card">
          <template #header>
            <div class="card-header">
              <span>实验参数</span>
              <el-icon><Setting /></el-icon>
            </div>
          </template>
          
          <el-form :model="parameters" label-width="120px">
            <el-form-item label="实验类型">
              <el-select v-model="experimentType" @change="onTypeChange">
                <el-option label="循环伏安法 (CV)" value="CV"></el-option>
                <el-option label="线性伏安法 (LSV)" value="LSV"></el-option>
                <el-option label="方波伏安法 (SWV)" value="SWV"></el-option>
              </el-select>
            </el-form-item>
            
            <el-form-item label="起始电压 (V)">
              <el-input-number 
                v-model="parameters.startVoltage"
                :precision="3"
                :step="0.1"
                :min="-3"
                :max="3"
                size="small" />
            </el-form-item>
            
            <el-form-item label="结束电压 (V)">
              <el-input-number 
                v-model="parameters.endVoltage"
                :precision="3"
                :step="0.1"
                :min="-3"
                :max="3"
                size="small" />
            </el-form-item>
            
            <el-form-item label="扫描速率 (mV/s)">
              <el-input-number 
                v-model="parameters.scanRate"
                :precision="0"
                :step="10"
                :min="1"
                :max="1000"
                size="small" />
            </el-form-item>
            
            <el-form-item label="循环次数" v-if="experimentType === 'CV'">
              <el-input-number 
                v-model="parameters.cycles"
                :precision="0"
                :step="1"
                :min="1"
                :max="10"
                size="small" />
            </el-form-item>
            
            <el-form-item label="振幅 (V)" v-if="experimentType === 'SWV'">
              <el-input-number 
                v-model="parameters.amplitude"
                :precision="3"
                :step="0.001"
                :min="0.001"
                :max="0.1"
                size="small" />
            </el-form-item>
            
            <el-form-item label="频率 (Hz)" v-if="experimentType === 'SWV'">
              <el-input-number 
                v-model="parameters.frequency"
                :precision="0"
                :step="1"
                :min="1"
                :max="100"
                size="small" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="updateParameters">
                更新参数
              </el-button>
              <el-button @click="resetParameters">
                重置参数
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <!-- 实验控制 -->
      <el-col :span="16">
        <el-card class="control-card">
          <template #header>
            <div class="card-header">
              <span>实验控制</span>
              <el-icon><DataAnalysis /></el-icon>
            </div>
          </template>
          
          <div class="control-panel">
            <div class="control-buttons">
              <el-button 
                type="success"
                size="large"
                :disabled="!bluetoothConnected || isRunning"
                @click="startExperiment">
                <el-icon><VideoPlay /></el-icon>
                开始实验
              </el-button>
              
              <el-button 
                type="warning"
                size="large"
                :disabled="!isRunning"
                @click="pauseExperiment">
                <el-icon><VideoPause /></el-icon>
                暂停实验
              </el-button>
              
              <el-button 
                type="danger"
                size="large"
                :disabled="!isRunning"
                @click="stopExperiment">
                <el-icon><VideoStop /></el-icon>
                停止实验
              </el-button>
            </div>
            
            <div class="experiment-info" v-if="currentExperiment">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="实验ID">
                  {{ currentExperiment.id }}
                </el-descriptions-item>
                <el-descriptions-item label="实验类型">
                  {{ currentExperiment.type }}
                </el-descriptions-item>
                <el-descriptions-item label="开始时间">
                  {{ formatTime(currentExperiment.startTime) }}
                </el-descriptions-item>
                <el-descriptions-item label="运行时间">
                  {{ runningTime }}
                </el-descriptions-item>
                <el-descriptions-item label="数据点数">
                  {{ realTimeData.length }}
                </el-descriptions-item>
                <el-descriptions-item label="状态">
                  <el-tag :type="statusType">{{ statusText }}</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 实时数据图表 -->
    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>实时数据</span>
              <div class="chart-actions">
                <el-button size="small" @click="exportChart">
                  <el-icon><Download /></el-icon>
                  导出图表
                </el-button>
                <el-button size="small" @click="clearChart">
                  <el-icon><Delete /></el-icon>
                  清空图表
                </el-button>
              </div>
            </div>
          </template>
          
          <ElectrochemicalChart 
            ref="chart"
            :data="realTimeData"
            :type="experimentType"
            :real-time="true"
            :title="`${experimentType} 实时数据`"
            height="400px" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'
import ElectrochemicalChart from '@/components/ElectrochemicalChart.vue'

export default {
  name: 'Experiment',
  components: {
    ElectrochemicalChart
  },
  data() {
    return {
      parameters: {
        startVoltage: 0,
        endVoltage: 1,
        scanRate: 100,
        cycles: 1,
        amplitude: 0.025,
        frequency: 25
      },
      experimentType: 'CV',
      timer: null,
      startTime: null
    }
  },
  computed: {
    ...mapState('bluetooth', ['bluetoothConnected']),
    ...mapState('experiment', ['isRunning', 'realTimeData', 'currentExperiment']),
    ...mapGetters('experiment', ['experimentInProgress']),
    
    statusType() {
      if (this.isRunning) return 'success'
      if (this.currentExperiment) return 'warning'
      return 'info'
    },
    
    statusText() {
      if (this.isRunning) return '运行中'
      if (this.currentExperiment) return '已完成'
      return '未开始'
    },
    
    runningTime() {
      if (!this.currentExperiment || !this.isRunning) return '0s'
      if (!this.startTime) return '0s'
      
      const now = new Date()
      const duration = Math.floor((now - this.startTime) / 1000)
      const minutes = Math.floor(duration / 60)
      const seconds = duration % 60
      
      return `${minutes}m ${seconds}s`
    }
  },
  
  watch: {
    isRunning(newVal) {
      if (newVal) {
        this.startTime = new Date()
        this.timer = setInterval(() => {
          this.$forceUpdate()
        }, 1000)
      } else {
        if (this.timer) {
          clearInterval(this.timer)
          this.timer = null
        }
        this.startTime = null
      }
    }
  },
  
  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer)
    }
  },
  
  methods: {
    onTypeChange(type) {
      this.experimentType = type
      this.$store.commit('experiment/SET_EXPERIMENT_TYPE', type)
    },
    
    async updateParameters() {
      try {
        await this.$store.dispatch('experiment/updateParameters', this.parameters)
        this.$message.success('参数更新成功')
      } catch (error) {
        this.$message.error('参数更新失败: ' + error.message)
      }
    },
    
    resetParameters() {
      this.parameters = {
        startVoltage: 0,
        endVoltage: 1,
        scanRate: 100,
        cycles: 1,
        amplitude: 0.025,
        frequency: 25
      }
    },
    
    async startExperiment() {
      if (!this.bluetoothConnected) {
        this.$message.error('请先连接蓝牙设备')
        return
      }
      
      try {
        await this.updateParameters()
        await this.$store.dispatch('experiment/startExperiment')
        this.$message.success('实验已开始')
      } catch (error) {
        this.$message.error('启动实验失败: ' + error.message)
      }
    },
    
    async pauseExperiment() {
      // 暂停功能待实现
      this.$message.info('暂停功能开发中...')
    },
    
    async stopExperiment() {
      try {
        await this.$store.dispatch('experiment/stopExperiment')
        this.$message.success('实验已停止')
      } catch (error) {
        this.$message.error('停止实验失败: ' + error.message)
      }
    },
    
    exportChart() {
      if (this.$refs.chart) {
        this.$refs.chart.exportChart()
      }
    },
    
    clearChart() {
      if (this.$refs.chart) {
        this.$refs.chart.clearChart()
      }
    },
    
    formatTime(time) {
      return new Date(time).toLocaleString()
    }
  }
}
</script>

<style scoped>
.experiment {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-panel {
  text-align: center;
}

.control-buttons {
  margin-bottom: 20px;
}

.control-buttons .el-button {
  margin: 0 10px;
}

.experiment-info {
  margin-top: 20px;
}

.chart-actions {
  display: flex;
  gap: 10px;
}

.parameter-card {
  height: fit-content;
}

.el-form-item {
  margin-bottom: 20px;
}
</style>
