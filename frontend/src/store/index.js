import { createStore } from 'vuex'
import bluetooth from './modules/bluetooth'
import experiment from './modules/experiment'
import data from './modules/data'

export default createStore({
  modules: {
    bluetooth,
    experiment,
    data
  }
})
