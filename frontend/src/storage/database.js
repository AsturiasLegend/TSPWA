import Dexie from 'dexie'

export class ElectrochemicalDB extends Dexie {
  constructor() {
    super('ElectrochemicalDB')
    
    this.version(1).stores({
      experiments: '++id, type, startTime, endTime, parameters, data, status, tags',
      settings: '++id, key, value',
      calibrations: '++id, deviceId, type, parameters, createdAt'
    })
  }
}

export const db = new ElectrochemicalDB()

// 数据库工具函数
export const dbUtils = {
  async saveExperiment(experiment) {
    return await db.experiments.add(experiment)
  },
  
  async getExperiments(filters = {}) {
    let query = db.experiments.orderBy('startTime').reverse()
    
    if (filters.type) {
      query = query.filter(exp => exp.type === filters.type)
    }
    
    if (filters.dateRange) {
      const [start, end] = filters.dateRange
      query = query.filter(exp => {
        const date = new Date(exp.startTime)
        return date >= start && date <= end
      })
    }
    
    return await query.toArray()
  },
  
  async deleteExperiment(id) {
    return await db.experiments.delete(id)
  },
  
  async updateExperiment(id, changes) {
    return await db.experiments.update(id, changes)
  },
  
  async getSetting(key) {
    const setting = await db.settings.where('key').equals(key).first()
    return setting ? setting.value : null
  },
  
  async setSetting(key, value) {
    const existing = await db.settings.where('key').equals(key).first()
    if (existing) {
      return await db.settings.update(existing.id, { value })
    } else {
      return await db.settings.add({ key, value })
    }
  },
  
  async clearAllData() {
    await db.experiments.clear()
    await db.settings.clear()
    await db.calibrations.clear()
  },
  
  async exportData() {
    const experiments = await db.experiments.toArray()
    const settings = await db.settings.toArray()
    const calibrations = await db.calibrations.toArray()
    
    return {
      experiments,
      settings,
      calibrations,
      exportDate: new Date().toISOString()
    }
  },
  
  async importData(data) {
    if (data.experiments) {
      await db.experiments.bulkAdd(data.experiments)
    }
    if (data.settings) {
      await db.settings.bulkAdd(data.settings)
    }
    if (data.calibrations) {
      await db.calibrations.bulkAdd(data.calibrations)
    }
  }
}
