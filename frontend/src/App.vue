<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 移动端头部 -->
      <el-header class="mobile-header">
        <div class="header-content">
          <div class="header-left">
            <el-button 
              v-if="isMobile" 
              @click="toggleDrawer"
              class="menu-button"
              text>
              <el-icon><Menu /></el-icon>
            </el-button>
            <h1 class="app-title">电化学工作站</h1>
          </div>
          <div class="connection-status">
            <el-badge :value="connectedDevices" class="item">
              <el-button 
                :type="bluetoothConnected ? 'success' : 'info'" 
                @click="toggleBluetooth"
                :size="isMobile ? 'small' : 'default'">
                <el-icon><Connection /></el-icon>
                <span v-if="!isMobile">{{ bluetoothConnected ? '已连接' : '未连接' }}</span>
              </el-button>
            </el-badge>
          </div>
        </div>
      </el-header>
      
      <el-container class="main-container">
        <!-- 桌面端侧边栏 -->
        <el-aside v-if="!isMobile" width="200px" class="desktop-aside">
          <el-menu
            :default-active="$route.path"
            router
            background-color="#545c64"
            text-color="#fff"
            active-text-color="#ffd04b">
            <el-menu-item index="/">
              <el-icon><House /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/experiment">
              <el-icon><DataAnalysis /></el-icon>
              <span>实验控制</span>
            </el-menu-item>
            <el-menu-item index="/data">
              <el-icon><Document /></el-icon>
              <span>数据管理</span>
            </el-menu-item>
            <el-menu-item index="/settings">
              <el-icon><Setting /></el-icon>
              <span>设置</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        
        <!-- 移动端抽屉导航 -->
        <el-drawer
          v-model="drawerVisible"
          :with-header="false"
          :size="250"
          direction="ltr">
          <el-menu
            :default-active="$route.path"
            router
            background-color="#545c64"
            text-color="#fff"
            active-text-color="#ffd04b"
            @select="handleMenuSelect">
            <el-menu-item index="/">
              <el-icon><House /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/experiment">
              <el-icon><DataAnalysis /></el-icon>
              <span>实验控制</span>
            </el-menu-item>
            <el-menu-item index="/data">
              <el-icon><Document /></el-icon>
              <span>数据管理</span>
            </el-menu-item>
            <el-menu-item index="/settings">
              <el-icon><Setting /></el-icon>
              <span>设置</span>
            </el-menu-item>
          </el-menu>
        </el-drawer>
        
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>
      
      <!-- 移动端底部导航 -->
      <el-footer v-if="isMobile" class="mobile-footer">
        <div class="bottom-nav">
          <div 
            :class="['nav-item', { active: $route.path === '/' }]"
            @click="$router.push('/')">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </div>
          <div 
            :class="['nav-item', { active: $route.path === '/experiment' }]"
            @click="$router.push('/experiment')">
            <el-icon><DataAnalysis /></el-icon>
            <span>实验</span>
          </div>
          <div 
            :class="['nav-item', { active: $route.path === '/data' }]"
            @click="$router.push('/data')">
            <el-icon><Document /></el-icon>
            <span>数据</span>
          </div>
          <div 
            :class="['nav-item', { active: $route.path === '/settings' }]"
            @click="$router.push('/settings')">
            <el-icon><Setting /></el-icon>
            <span>设置</span>
          </div>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import { mapState } from 'vuex'
// eslint-disable-next-line no-unused-vars
import { Menu, House, DataAnalysis, Document, Setting } from '@element-plus/icons-vue'

export default {
  name: 'App',
  data() {
    return {
      drawerVisible: false,
      isMobile: false
    }
  },
  computed: {
    ...mapState('bluetooth', ['bluetoothConnected', 'connectedDevices'])
  },
  methods: {
    toggleBluetooth() {
      if (this.bluetoothConnected) {
        this.$store.dispatch('bluetooth/disconnect')
      } else {
        this.$store.dispatch('bluetooth/connect')
      }
    },
    toggleDrawer() {
      this.drawerVisible = !this.drawerVisible
    },
    handleMenuSelect() {
      this.drawerVisible = false
    },
    checkMobile() {
      this.isMobile = window.innerWidth <= 768
    }
  },
  mounted() {
    this.checkMobile()
    window.addEventListener('resize', this.checkMobile)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkMobile)
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  overflow: hidden;
}

.app-container {
  height: 100vh;
}

/* 移动端头部样式 */
.mobile-header {
  background-color: #409EFF;
  color: white;
  padding: 0 16px;
  height: 60px !important;
  line-height: 60px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header-left {
  display: flex;
  align-items: center;
}

.menu-button {
  margin-right: 12px;
  color: white !important;
}

.app-title {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.connection-status .el-button {
  border: none;
}

/* 主容器样式 */
.main-container {
  flex: 1;
  margin-top: 60px;
  margin-bottom: 60px;
}

/* 桌面端侧边栏 */
.desktop-aside {
  background-color: #545c64;
  position: fixed;
  top: 60px;
  left: 0;
  bottom: 0;
  z-index: 999;
}

/* 主内容区域 */
.app-main {
  padding: 16px;
  overflow-y: auto;
  height: calc(100vh - 120px);
}

/* 移动端底部导航 */
.mobile-footer {
  background-color: #ffffff;
  border-top: 1px solid #ebeef5;
  padding: 0;
  height: 60px !important;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.bottom-nav {
  display: flex;
  height: 100%;
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #909399;
  font-size: 12px;
}

.nav-item.active {
  color: #409EFF;
}

.nav-item:hover {
  background-color: #f5f7fa;
}

.nav-item .el-icon {
  font-size: 20px;
  margin-bottom: 2px;
}

/* 响应式布局 */
@media (min-width: 769px) {
  .main-container {
    margin-top: 60px;
    margin-bottom: 0;
  }
  
  .app-main {
    margin-left: 200px;
    height: calc(100vh - 60px);
  }
  
  .mobile-footer {
    display: none;
  }
}

@media (max-width: 768px) {
  .desktop-aside {
    display: none;
  }
  
  .app-title {
    font-size: 16px;
  }
  
  .header-content {
    padding: 0 8px;
  }
  
  .app-main {
    padding: 12px;
  }
}

/* 抽屉样式 */
.el-drawer__body {
  padding: 0;
}

.el-drawer .el-menu {
  border: none;
}

/* 加载状态 */
.el-loading-mask {
  z-index: 2000;
}

/* 卡片样式优化 */
.el-card {
  margin-bottom: 16px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 表格响应式 */
.el-table {
  font-size: 14px;
}

@media (max-width: 768px) {
  .el-table {
    font-size: 12px;
  }
  
  .el-table .el-table__cell {
    padding: 8px 0;
  }
}

/* 表单响应式 */
.el-form-item {
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .el-form-item {
    margin-bottom: 12px;
  }
  
  .el-form-item__label {
    font-size: 14px;
  }
}

/* 按钮响应式 */
@media (max-width: 768px) {
  .el-button {
    padding: 8px 15px;
    font-size: 14px;
  }
  
  .el-button--small {
    padding: 6px 12px;
    font-size: 12px;
  }
}

/* 图表容器响应式 */
.chart-container {
  width: 100%;
  height: 400px;
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .chart-container {
    height: 300px;
  }
}
</style>
