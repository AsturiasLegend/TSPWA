import BluetoothService from '@/bluetooth/BluetoothService'

const state = {
  bluetoothSupported: false,
  bluetoothConnected: false,
  connectedDevices: 0,
  deviceInfo: null,
  receivedData: []
}

const mutations = {
  SET_BLUETOOTH_SUPPORTED(state, supported) {
    state.bluetoothSupported = supported
  },
  SET_BLUETOOTH_CONNECTED(state, connected) {
    state.bluetoothConnected = connected
  },
  SET_CONNECTED_DEVICES(state, count) {
    state.connectedDevices = count
  },
  SET_DEVICE_INFO(state, info) {
    state.deviceInfo = info
  },
  ADD_RECEIVED_DATA(state, data) {
    state.receivedData.push(data)
  },
  CLEAR_RECEIVED_DATA(state) {
    state.receivedData = []
  }
}

const actions = {
  async initBluetooth({ commit }) {
    const supported = BluetoothService.isSupported()
    commit('SET_BLUETOOTH_SUPPORTED', supported)
    return supported
  },
  
  async connect({ commit }) {
    try {
      const device = await BluetoothService.connect()
      commit('SET_BLUETOOTH_CONNECTED', true)
      commit('SET_CONNECTED_DEVICES', 1)
      commit('SET_DEVICE_INFO', device)
      
      // 设置数据接收回调
      BluetoothService.onDataReceived((data) => {
        commit('ADD_RECEIVED_DATA', data)
      })
      
      return device
    } catch (error) {
      console.error('Bluetooth connection failed:', error)
      throw error
    }
  },
  
  async disconnect({ commit }) {
    try {
      await BluetoothService.disconnect()
      commit('SET_BLUETOOTH_CONNECTED', false)
      commit('SET_CONNECTED_DEVICES', 0)
      commit('SET_DEVICE_INFO', null)
    } catch (error) {
      console.error('Bluetooth disconnection failed:', error)
      throw error
    }
  },
  
  async sendCommand({ state }, command) {
    if (!state.bluetoothConnected) {
      throw new Error('Bluetooth not connected')
    }
    return await BluetoothService.sendCommand(command)
  }
}

const getters = {
  isBluetoothReady: (state) => state.bluetoothSupported && state.bluetoothConnected,
  latestData: (state) => state.receivedData.slice(-1)[0] || null
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
