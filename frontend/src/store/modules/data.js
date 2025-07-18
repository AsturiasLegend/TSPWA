import { db } from '@/storage/database'

const state = {
  experiments: [],
  currentExperiment: null,
  filters: {
    type: '',
    dateRange: [],
    tags: []
  }
}

const mutations = {
  SET_EXPERIMENTS(state, experiments) {
    state.experiments = experiments
  },
  SET_CURRENT_EXPERIMENT(state, experiment) {
    state.currentExperiment = experiment
  },
  ADD_EXPERIMENT(state, experiment) {
    state.experiments.unshift(experiment)
  },
  UPDATE_EXPERIMENT(state, experiment) {
    const index = state.experiments.findIndex(e => e.id === experiment.id)
    if (index !== -1) {
      state.experiments.splice(index, 1, experiment)
    }
  },
  DELETE_EXPERIMENT(state, id) {
    state.experiments = state.experiments.filter(e => e.id !== id)
  },
  SET_FILTERS(state, filters) {
    state.filters = { ...state.filters, ...filters }
  }
}

const actions = {
  async loadExperiments({ commit }) {
    try {
      const experiments = await db.experiments.orderBy('startTime').reverse().toArray()
      commit('SET_EXPERIMENTS', experiments)
      return experiments
    } catch (error) {
      console.error('Failed to load experiments:', error)
      throw error
    }
  },
  
  async saveExperiment({ commit }, experiment) {
    try {
      const id = await db.experiments.add(experiment)
      const savedExperiment = { ...experiment, id }
      commit('ADD_EXPERIMENT', savedExperiment)
      return savedExperiment
    } catch (error) {
      console.error('Failed to save experiment:', error)
      throw error
    }
  },
  
  async updateExperiment({ commit }, experiment) {
    try {
      await db.experiments.update(experiment.id, experiment)
      commit('UPDATE_EXPERIMENT', experiment)
      return experiment
    } catch (error) {
      console.error('Failed to update experiment:', error)
      throw error
    }
  },
  
  async deleteExperiment({ commit }, id) {
    try {
      await db.experiments.delete(id)
      commit('DELETE_EXPERIMENT', id)
    } catch (error) {
      console.error('Failed to delete experiment:', error)
      throw error
    }
  },
  
  async exportExperiment({ state }, id) {
    const experiment = state.experiments.find(e => e.id === id)
    if (!experiment) {
      throw new Error('Experiment not found')
    }
    
    const csvData = this.generateCSV(experiment)
    const blob = new Blob([csvData], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    
    const a = document.createElement('a')
    a.href = url
    a.download = `experiment_${id}_${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    
    URL.revokeObjectURL(url)
  },
  
  generateCSV(experiment) {
    const headers = ['Time', 'Voltage', 'Current']
    const rows = [headers.join(',')]
    
    experiment.data.forEach(point => {
      rows.push(`${point.time},${point.voltage},${point.current}`)
    })
    
    return rows.join('\n')
  }
}

const getters = {
  filteredExperiments: (state) => {
    let filtered = state.experiments
    
    if (state.filters.type) {
      filtered = filtered.filter(e => e.type === state.filters.type)
    }
    
    if (state.filters.dateRange.length === 2) {
      const [start, end] = state.filters.dateRange
      filtered = filtered.filter(e => {
        const date = new Date(e.startTime)
        return date >= start && date <= end
      })
    }
    
    return filtered
  },
  
  experimentTypes: (state) => {
    const types = new Set(state.experiments.map(e => e.type))
    return Array.from(types)
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
