const state = {
  currentExperiment: null,
  experimentType: 'CV', // CV, LSV, SWV等
  parameters: {
    startVoltage: 0,
    endVoltage: 1,
    scanRate: 100,
    cycles: 1
  },
  isRunning: false,
  realTimeData: [],
  experimentHistory: []
}

const mutations = {
  SET_EXPERIMENT_TYPE(state, type) {
    state.experimentType = type
  },
  SET_PARAMETERS(state, params) {
    state.parameters = { ...state.parameters, ...params }
  },
  SET_RUNNING(state, running) {
    state.isRunning = running
  },
  ADD_REAL_TIME_DATA(state, data) {
    state.realTimeData.push(data)
  },
  CLEAR_REAL_TIME_DATA(state) {
    state.realTimeData = []
  },
  SET_CURRENT_EXPERIMENT(state, experiment) {
    state.currentExperiment = experiment
  },
  ADD_EXPERIMENT_HISTORY(state, experiment) {
    state.experimentHistory.unshift(experiment)
  }
}

const actions = {
  async startExperiment({ commit, state, dispatch }) {
    if (state.isRunning) {
      throw new Error('Experiment already running')
    }
    
    const experiment = {
      id: Date.now(),
      type: state.experimentType,
      parameters: { ...state.parameters },
      startTime: new Date(),
      data: [],
      status: 'running'
    }
    
    commit('SET_CURRENT_EXPERIMENT', experiment)
    commit('SET_RUNNING', true)
    commit('CLEAR_REAL_TIME_DATA')
    
    // 发送开始命令到蓝牙设备
    const command = {
      type: 'START_EXPERIMENT',
      experimentType: state.experimentType,
      parameters: state.parameters
    }
    
    try {
      await dispatch('bluetooth/sendCommand', command, { root: true })
      return experiment
    } catch (error) {
      commit('SET_RUNNING', false)
      throw error
    }
  },
  
  async stopExperiment({ commit, state }) {
    if (!state.isRunning) {
      return
    }
    
    commit('SET_RUNNING', false)
    
    if (state.currentExperiment) {
      const completedExperiment = {
        ...state.currentExperiment,
        endTime: new Date(),
        data: [...state.realTimeData],
        status: 'completed'
      }
      
      commit('ADD_EXPERIMENT_HISTORY', completedExperiment)
      commit('SET_CURRENT_EXPERIMENT', null)
      
      // 保存到本地存储
      await this.dispatch('data/saveExperiment', completedExperiment, { root: true })
    }
    
    // 发送停止命令到蓝牙设备
    const command = { type: 'STOP_EXPERIMENT' }
    return await this.dispatch('bluetooth/sendCommand', command, { root: true })
  },
  
  updateParameters({ commit }, params) {
    commit('SET_PARAMETERS', params)
  },
  
  addDataPoint({ commit }, dataPoint) {
    commit('ADD_REAL_TIME_DATA', dataPoint)
  }
}

const getters = {
  experimentInProgress: (state) => state.isRunning && state.currentExperiment,
  currentExperimentData: (state) => state.realTimeData,
  recentExperiments: (state) => state.experimentHistory.slice(0, 10)
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
