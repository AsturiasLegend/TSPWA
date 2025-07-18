<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>电化学工作站</h1>
          <div class="connection-status">
            <el-badge :value="connectedDevices" class="item">
              <el-button :type="bluetoothConnected ? 'success' : 'info'" @click="toggleBluetooth">
                <el-icon><Connection /></el-icon>
                {{ bluetoothConnected ? '已连接' : '未连接' }}
              </el-button>
            </el-badge>
          </div>
        </div>
      </el-header>
      
      <el-container>
        <el-aside width="200px">
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
        
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'App',
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
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header-content h1 {
  margin: 0;
  color: #409EFF;
}

.el-aside {
  background-color: #545c64;
}

.el-main {
  padding: 20px;
}
</style>
