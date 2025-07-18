import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Experiment from '@/views/Experiment.vue'
import DataManagement from '@/views/DataManagement.vue'
import Settings from '@/views/Settings.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/experiment',
    name: 'Experiment',
    component: Experiment
  },
  {
    path: '/data',
    name: 'DataManagement',
    component: DataManagement
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
