class BluetoothService {
  constructor() {
    this.device = null
    this.server = null
    this.service = null
    this.writeCharacteristic = null
    this.readCharacteristic = null
    this.dataCallback = null
    
    // MSP430 蓝牙服务 UUID (需要根据实际硬件调整)
    this.serviceUUID = '12345678-1234-1234-1234-123456789abc'
    this.writeCharacteristicUUID = '12345678-1234-1234-1234-123456789abd'
    this.readCharacteristicUUID = '12345678-1234-1234-1234-123456789abe'
  }
  
  isSupported() {
    return 'bluetooth' in navigator && 'requestDevice' in navigator.bluetooth
  }
  
  async connect() {
    if (!this.isSupported()) {
      throw new Error('Web Bluetooth API not supported')
    }
    
    try {
      // 请求蓝牙设备
      this.device = await navigator.bluetooth.requestDevice({
        filters: [
          { services: [this.serviceUUID] }
        ],
        optionalServices: [this.serviceUUID]
      })
      
      // 监听断开连接事件
      this.device.addEventListener('gattserverdisconnected', this.onDisconnected.bind(this))
      
      // 连接到GATT服务器
      this.server = await this.device.gatt.connect()
      
      // 获取主服务
      this.service = await this.server.getPrimaryService(this.serviceUUID)
      
      // 获取特征值
      this.writeCharacteristic = await this.service.getCharacteristic(this.writeCharacteristicUUID)
      this.readCharacteristic = await this.service.getCharacteristic(this.readCharacteristicUUID)
      
      // 启用通知
      await this.readCharacteristic.startNotifications()
      this.readCharacteristic.addEventListener('characteristicvaluechanged', this.onDataReceived.bind(this))
      
      console.log('Bluetooth connected successfully')
      return {
        name: this.device.name,
        id: this.device.id,
        connected: true
      }
    } catch (error) {
      console.error('Bluetooth connection failed:', error)
      throw error
    }
  }
  
  async disconnect() {
    if (this.device && this.device.gatt.connected) {
      await this.device.gatt.disconnect()
    }
    this.cleanup()
  }
  
  onDisconnected() {
    console.log('Bluetooth device disconnected')
    this.cleanup()
    
    // 可以在这里触发重连逻辑
    if (this.disconnectCallback) {
      this.disconnectCallback()
    }
  }
  
  cleanup() {
    this.device = null
    this.server = null
    this.service = null
    this.writeCharacteristic = null
    this.readCharacteristic = null
  }
  
  async sendCommand(command) {
    if (!this.writeCharacteristic) {
      throw new Error('Bluetooth not connected')
    }
    
    const commandString = JSON.stringify(command)
    const encoder = new TextEncoder()
    const data = encoder.encode(commandString)
    
    try {
      await this.writeCharacteristic.writeValue(data)
      console.log('Command sent:', command)
      return true
    } catch (error) {
      console.error('Failed to send command:', error)
      throw error
    }
  }
  
  onDataReceived(event) {
    const decoder = new TextDecoder()
    const data = decoder.decode(event.target.value)
    
    try {
      const parsedData = JSON.parse(data)
      console.log('Data received:', parsedData)
      
      if (this.dataCallback) {
        this.dataCallback(parsedData)
      }
    } catch (error) {
      console.error('Failed to parse received data:', error)
    }
  }
  
  setDataCallback(callback) {
    this.dataCallback = callback
  }
  
  setDisconnectCallback(callback) {
    this.disconnectCallback = callback
  }
  
  isConnected() {
    return this.device && this.device.gatt.connected
  }
}

export default new BluetoothService()
