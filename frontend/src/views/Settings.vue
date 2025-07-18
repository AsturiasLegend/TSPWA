<template>
  <div class="settings">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>蓝牙设置</span>
              <el-icon><Connection /></el-icon>
            </div>
          </template>
          
          <el-form :model="bluetoothSettings" label-width="120px">
            <el-form-item label="自动连接">
              <el-switch v-model="bluetoothSettings.autoConnect" />
            </el-form-item>
            
            <el-form-item label="连接超时(秒)">
              <el-input-number 
                v-model="bluetoothSettings.connectionTimeout"
                :min="5"
                :max="30"
                :step="1" />
            </el-form-item>
            
            <el-form-item label="重连间隔(秒)">
              <el-input-number 
                v-model="bluetoothSettings.reconnectInterval"
                :min="1"
                :max="60"
                :step="1" />
            </el-form-item>
            
            <el-form-item label="最大重连次数">
              <el-input-number 
                v-model="bluetoothSettings.maxReconnectAttempts"
                :min="0"
                :max="10"
                :step="1" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>实验设置</span>
              <el-icon><DataAnalysis /></el-icon>
            </div>
          </template>
          
          <el-form :model="experimentSettings" label-width="120px">
            <el-form-item label="自动保存">
              <el-switch v-model="experimentSettings.autoSave" />
            </el-form-item>
            
            <el-form-item label="数据采样率(Hz)">
              <el-input-number 
                v-model="experimentSettings.samplingRate"
                :min="1"
                :max="1000"
                :step="1" />
            </el-form-item>
            
            <el-form-item label="最大数据点数">
              <el-input-number 
                v-model="experimentSettings.maxDataPoints"
                :min="1000"
                :max="100000"
                :step="1000" />
            </el-form-item>
            
            <el-form-item label="默认实验类型">
              <el-select v-model="experimentSettings.defaultExperimentType">
                <el-option label="循环伏安法 (CV)" value="CV" />
                <el-option label="线性伏安法 (LSV)" value="LSV" />
                <el-option label="方波伏安法 (SWV)" value="SWV" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>数据管理</span>
              <el-icon><Document /></el-icon>
            </div>
          </template>
          
          <el-form :model="dataSettings" label-width="120px">
            <el-form-item label="本地存储限制">
              <el-select v-model="dataSettings.storageLimit">
                <el-option label="100MB" value="100" />
                <el-option label="500MB" value="500" />
                <el-option label="1GB" value="1000" />
                <el-option label="5GB" value="5000" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="自动清理">
              <el-switch v-model="dataSettings.autoCleanup" />
            </el-form-item>
            
            <el-form-item label="保留天数">
              <el-input-number 
                v-model="dataSettings.retentionDays"
                :min="1"
                :max="365"
                :step="1"
                :disabled="!dataSettings.autoCleanup" />
            </el-form-item>
            
            <el-form-item label="云端同步">
              <el-switch v-model="dataSettings.cloudSync" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>界面设置</span>
              <el-icon><Setting /></el-icon>
            </div>
          </template>
          
          <el-form :model="uiSettings" label-width="120px">
            <el-form-item label="主题">
              <el-select v-model="uiSettings.theme">
                <el-option label="浅色" value="light" />
                <el-option label="深色" value="dark" />
                <el-option label="自动" value="auto" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="语言">
              <el-select v-model="uiSettings.language">
                <el-option label="中文" value="zh" />
                <el-option label="English" value="en" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="图表颜色">
              <el-select v-model="uiSettings.chartTheme">
                <el-option label="默认" value="default" />
                <el-option label="科学" value="scientific" />
                <el-option label="彩色" value="colorful" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="显示网格">
              <el-switch v-model="uiSettings.showGrid" />
            </el-form-item>
            
            <el-form-item label="显示动画">
              <el-switch v-model="uiSettings.showAnimation" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统信息</span>
              <el-icon><InfoFilled /></el-icon>
            </div>
          </template>
          
          <el-descriptions :column="3" border>
            <el-descriptions-item label="应用版本">
              {{ appVersion }}
            </el-descriptions-item>
            <el-descriptions-item label="构建时间">
              {{ buildTime }}
            </el-descriptions-item>
            <el-descriptions-item label="浏览器">
              {{ browserInfo }}
            </el-descriptions-item>
            <el-descriptions-item label="蓝牙支持">
              <el-tag :type="bluetoothSupported ? 'success' : 'danger'">
                {{ bluetoothSupported ? '支持' : '不支持' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="本地存储">
              {{ storageInfo }}
            </el-descriptions-item>
            <el-descriptions-item label="实验数据">
              {{ experimentCount }} 个实验
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
    
    <div class="actions">
      <el-button type="primary" @click="saveSettings">
        保存设置
      </el-button>
      <el-button @click="resetSettings">
        重置设置
      </el-button>
      <el-button type="danger" @click="clearAllData">
        清空所有数据
      </el-button>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'Settings',
  data() {
    return {
      bluetoothSettings: {
        autoConnect: true,
        connectionTimeout: 10,
        reconnectInterval: 5,
        maxReconnectAttempts: 3
      },
      experimentSettings: {
        autoSave: true,
        samplingRate: 100,
        maxDataPoints: 10000,
        defaultExperimentType: 'CV'
      },
      dataSettings: {
        storageLimit: '500',
        autoCleanup: false,
        retentionDays: 30,
        cloudSync: false
      },
      uiSettings: {
        theme: 'light',
        language: 'zh',
        chartTheme: 'default',
        showGrid: true,
        showAnimation: true
      }
    }
  },
  computed: {
    ...mapState('bluetooth', ['bluetoothSupported']),
    ...mapState('data', ['experiments']),
    
    appVersion() {
      return process.env.VUE_APP_VERSION || '1.0.0'
    },
    
    buildTime() {
      return process.env.VUE_APP_BUILD_TIME || new Date().toLocaleString()
    },
    
    browserInfo() {
      return navigator.userAgent.split(' ').slice(-2).join(' ')
    },
    
    storageInfo() {
      if ('storage' in navigator && 'estimate' in navigator.storage) {
        return '检查中...'
      }
      return '不支持'
    },
    
    experimentCount() {
      return this.experiments.length
    }
  },
  
  async mounted() {
    await this.loadSettings()
    await this.checkStorageInfo()
  },
  
  methods: {
    async loadSettings() {
      try {
        const { dbUtils } = await import('@/storage/database')
        
        const bluetoothSettings = await dbUtils.getSetting('bluetoothSettings')
        if (bluetoothSettings) {
          this.bluetoothSettings = { ...this.bluetoothSettings, ...bluetoothSettings }
        }
        
        const experimentSettings = await dbUtils.getSetting('experimentSettings')
        if (experimentSettings) {
          this.experimentSettings = { ...this.experimentSettings, ...experimentSettings }
        }
        
        const dataSettings = await dbUtils.getSetting('dataSettings')
        if (dataSettings) {
          this.dataSettings = { ...this.dataSettings, ...dataSettings }
        }
        
        const uiSettings = await dbUtils.getSetting('uiSettings')
        if (uiSettings) {
          this.uiSettings = { ...this.uiSettings, ...uiSettings }
        }
      } catch (error) {
        console.error('Failed to load settings:', error)
      }
    },
    
    async saveSettings() {
      try {
        const { dbUtils } = await import('@/storage/database')
        
        await dbUtils.setSetting('bluetoothSettings', this.bluetoothSettings)
        await dbUtils.setSetting('experimentSettings', this.experimentSettings)
        await dbUtils.setSetting('dataSettings', this.dataSettings)
        await dbUtils.setSetting('uiSettings', this.uiSettings)
        
        this.$message.success('设置保存成功')
      } catch (error) {
        this.$message.error('设置保存失败: ' + error.message)
      }
    },
    
    async resetSettings() {
      try {
        await this.$confirm('确定要重置所有设置吗?', '确认重置', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        // 重置为默认值
        this.bluetoothSettings = {
          autoConnect: true,
          connectionTimeout: 10,
          reconnectInterval: 5,
          maxReconnectAttempts: 3
        }
        
        this.experimentSettings = {
          autoSave: true,
          samplingRate: 100,
          maxDataPoints: 10000,
          defaultExperimentType: 'CV'
        }
        
        this.dataSettings = {
          storageLimit: '500',
          autoCleanup: false,
          retentionDays: 30,
          cloudSync: false
        }
        
        this.uiSettings = {
          theme: 'light',
          language: 'zh',
          chartTheme: 'default',
          showGrid: true,
          showAnimation: true
        }
        
        await this.saveSettings()
        this.$message.success('设置重置成功')
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('设置重置失败: ' + error.message)
        }
      }
    },
    
    async clearAllData() {
      try {
        await this.$confirm('确定要清空所有数据吗? 此操作不可恢复!', '确认清空', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        const { dbUtils } = await import('@/storage/database')
        await dbUtils.clearAllData()
        
        await this.$store.dispatch('data/loadExperiments')
        this.$message.success('数据清空成功')
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('数据清空失败: ' + error.message)
        }
      }
    },
    
    async checkStorageInfo() {
      if ('storage' in navigator && 'estimate' in navigator.storage) {
        try {
          const estimate = await navigator.storage.estimate()
          const used = (estimate.usage / 1024 / 1024).toFixed(2)
          const total = (estimate.quota / 1024 / 1024).toFixed(2)
          this.storageInfo = `${used}MB / ${total}MB`
        } catch (error) {
          this.storageInfo = '检查失败'
        }
      }
    }
  }
}
</script>

<style scoped>
.settings {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions {
  margin-top: 20px;
  text-align: center;
}

.actions .el-button {
  margin: 0 10px;
}
</style>
