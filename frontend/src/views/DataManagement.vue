<template>
  <div class="data-management">
    <el-row :gutter="20">
      <!-- 筛选面板 -->
      <el-col :span="6">
        <el-card class="filter-card">
          <template #header>
            <div class="card-header">
              <span>数据筛选</span>
              <el-icon><Filter /></el-icon>
            </div>
          </template>
          
          <el-form :model="filters" label-width="80px">
            <el-form-item label="实验类型">
              <el-select v-model="filters.type" clearable placeholder="全部类型">
                <el-option 
                  v-for="type in experimentTypes"
                  :key="type"
                  :label="type"
                  :value="type">
                </el-option>
              </el-select>
            </el-form-item>
            
            <el-form-item label="日期范围">
              <el-date-picker
                v-model="filters.dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                size="small">
              </el-date-picker>
            </el-form-item>
            
            <el-form-item label="标签">
              <el-select v-model="filters.tags" multiple placeholder="选择标签">
                <el-option 
                  v-for="tag in availableTags"
                  :key="tag"
                  :label="tag"
                  :value="tag">
                </el-option>
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="applyFilters">
                应用筛选
              </el-button>
              <el-button @click="resetFilters">
                重置
              </el-button>
            </el-form-item>
          </el-form>
          
          <el-divider />
          
          <div class="data-actions">
            <el-button type="success" @click="exportAllData">
              <el-icon><Download /></el-icon>
              导出全部数据
            </el-button>
            <el-button type="warning" @click="importData">
              <el-icon><Upload /></el-icon>
              导入数据
            </el-button>
            <el-button type="danger" @click="clearAllData">
              <el-icon><Delete /></el-icon>
              清空数据
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <!-- 数据列表 -->
      <el-col :span="18">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>实验数据 ({{ filteredExperiments.length }})</span>
              <div class="table-actions">
                <el-input
                  v-model="searchText"
                  placeholder="搜索实验..."
                  size="small"
                  style="width: 200px">
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </div>
            </div>
          </template>
          
          <el-table
            :data="paginatedExperiments"
            style="width: 100%"
            @selection-change="handleSelectionChange"
            @row-click="viewExperiment">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="type" label="类型" width="80" />
            <el-table-column label="开始时间" width="180">
              <template #default="scope">
                {{ formatTime(scope.row.startTime) }}
              </template>
            </el-table-column>
            <el-table-column label="持续时间" width="100">
              <template #default="scope">
                {{ formatDuration(scope.row.startTime, scope.row.endTime) }}
              </template>
            </el-table-column>
            <el-table-column label="数据点数" width="100">
              <template #default="scope">
                {{ scope.row.data ? scope.row.data.length : 0 }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="80">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="标签" width="150">
              <template #default="scope">
                <el-tag 
                  v-for="tag in scope.row.tags"
                  :key="tag"
                  size="small"
                  style="margin-right: 5px">
                  {{ tag }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button size="small" @click="viewExperiment(scope.row)">
                  查看
                </el-button>
                <el-button size="small" @click="exportExperiment(scope.row.id)">
                  导出
                </el-button>
                <el-button size="small" type="danger" @click="deleteExperiment(scope.row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="filteredExperiments.length"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange">
            </el-pagination>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 实验详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="`实验详情 - ${currentExperimentDetail?.type} #${currentExperimentDetail?.id}`"
      width="80%"
      :destroy-on-close="true">
      <div v-if="currentExperimentDetail">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="实验ID">
                {{ currentExperimentDetail.id }}
              </el-descriptions-item>
              <el-descriptions-item label="实验类型">
                {{ currentExperimentDetail.type }}
              </el-descriptions-item>
              <el-descriptions-item label="开始时间">
                {{ formatTime(currentExperimentDetail.startTime) }}
              </el-descriptions-item>
              <el-descriptions-item label="结束时间">
                {{ formatTime(currentExperimentDetail.endTime) }}
              </el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="getStatusType(currentExperimentDetail.status)">
                  {{ currentExperimentDetail.status }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="数据点数">
                {{ currentExperimentDetail.data ? currentExperimentDetail.data.length : 0 }}
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
          <el-col :span="12">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="起始电压">
                {{ currentExperimentDetail.parameters?.startVoltage }} V
              </el-descriptions-item>
              <el-descriptions-item label="结束电压">
                {{ currentExperimentDetail.parameters?.endVoltage }} V
              </el-descriptions-item>
              <el-descriptions-item label="扫描速率">
                {{ currentExperimentDetail.parameters?.scanRate }} mV/s
              </el-descriptions-item>
              <el-descriptions-item label="循环次数" v-if="currentExperimentDetail.type === 'CV'">
                {{ currentExperimentDetail.parameters?.cycles }}
              </el-descriptions-item>
              <el-descriptions-item label="振幅" v-if="currentExperimentDetail.type === 'SWV'">
                {{ currentExperimentDetail.parameters?.amplitude }} V
              </el-descriptions-item>
              <el-descriptions-item label="频率" v-if="currentExperimentDetail.type === 'SWV'">
                {{ currentExperimentDetail.parameters?.frequency }} Hz
              </el-descriptions-item>
            </el-descriptions>
          </el-col>
        </el-row>
        
        <div style="margin-top: 20px;">
          <h4>实验数据图表</h4>
          <ElectrochemicalChart 
            :data="currentExperimentDetail.data || []"
            :type="currentExperimentDetail.type"
            :title="`${currentExperimentDetail.type} 实验数据`"
            height="400px" />
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="exportExperiment(currentExperimentDetail.id)">
            导出数据
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'
import ElectrochemicalChart from '@/components/ElectrochemicalChart.vue'

export default {
  name: 'DataManagement',
  components: {
    ElectrochemicalChart
  },
  data() {
    return {
      filters: {
        type: '',
        dateRange: [],
        tags: []
      },
      searchText: '',
      currentPage: 1,
      pageSize: 20,
      selectedExperiments: [],
      detailDialogVisible: false,
      currentExperimentDetail: null
    }
  },
  computed: {
    ...mapState('data', ['experiments']),
    ...mapGetters('data', ['filteredExperiments', 'experimentTypes']),
    
    availableTags() {
      const tags = new Set()
      this.experiments.forEach(exp => {
        if (exp.tags) {
          exp.tags.forEach(tag => tags.add(tag))
        }
      })
      return Array.from(tags)
    },
    
    searchedExperiments() {
      if (!this.searchText) {
        return this.filteredExperiments
      }
      
      const text = this.searchText.toLowerCase()
      return this.filteredExperiments.filter(exp => 
        exp.id.toString().includes(text) ||
        exp.type.toLowerCase().includes(text) ||
        (exp.tags && exp.tags.some(tag => tag.toLowerCase().includes(text)))
      )
    },
    
    paginatedExperiments() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.searchedExperiments.slice(start, end)
    }
  },
  
  async mounted() {
    await this.$store.dispatch('data/loadExperiments')
  },
  
  methods: {
    applyFilters() {
      this.$store.commit('data/SET_FILTERS', this.filters)
    },
    
    resetFilters() {
      this.filters = {
        type: '',
        dateRange: [],
        tags: []
      }
      this.applyFilters()
    },
    
    handleSelectionChange(selection) {
      this.selectedExperiments = selection
    },
    
    handleSizeChange(size) {
      this.pageSize = size
      this.currentPage = 1
    },
    
    handleCurrentChange(page) {
      this.currentPage = page
    },
    
    viewExperiment(row) {
      this.currentExperimentDetail = row
      this.detailDialogVisible = true
    },
    
    async exportExperiment(id) {
      try {
        await this.$store.dispatch('data/exportExperiment', id)
        this.$message.success('数据导出成功')
      } catch (error) {
        this.$message.error('导出失败: ' + error.message)
      }
    },
    
    async deleteExperiment(id) {
      try {
        await this.$confirm('确定要删除这个实验吗?', '确认删除', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await this.$store.dispatch('data/deleteExperiment', id)
        this.$message.success('实验删除成功')
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败: ' + error.message)
        }
      }
    },
    
    async exportAllData() {
      try {
        const { dbUtils } = await import('@/storage/database')
        const data = await dbUtils.exportData()
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        
        const a = document.createElement('a')
        a.href = url
        a.download = `experiments_export_${new Date().toISOString().split('T')[0]}.json`
        a.click()
        
        URL.revokeObjectURL(url)
        this.$message.success('数据导出成功')
      } catch (error) {
        this.$message.error('导出失败: ' + error.message)
      }
    },
    
    async importData() {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = '.json'
      
      input.onchange = async (e) => {
        const file = e.target.files[0]
        if (!file) return
        
        try {
          const text = await file.text()
          const data = JSON.parse(text)
          
          const { dbUtils } = await import('@/storage/database')
          await dbUtils.importData(data)
          
          await this.$store.dispatch('data/loadExperiments')
          this.$message.success('数据导入成功')
        } catch (error) {
          this.$message.error('导入失败: ' + error.message)
        }
      }
      
      input.click()
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
          this.$message.error('清空失败: ' + error.message)
        }
      }
    },
    
    formatTime(time) {
      if (!time) return '-'
      return new Date(time).toLocaleString()
    },
    
    formatDuration(start, end) {
      if (!start || !end) return '-'
      const duration = Math.floor((new Date(end) - new Date(start)) / 1000)
      const minutes = Math.floor(duration / 60)
      const seconds = duration % 60
      return `${minutes}m ${seconds}s`
    },
    
    getStatusType(status) {
      switch (status) {
        case 'completed': return 'success'
        case 'running': return 'warning'
        case 'error': return 'danger'
        default: return 'info'
      }
    }
  }
}
</script>

<style scoped>
.data-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-card {
  height: fit-content;
}

.data-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
