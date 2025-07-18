<template>
  <div class="chart-container">
    <div ref="chartDom" class="chart" :style="{ width: width, height: height }"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'ElectrochemicalChart',
  props: {
    data: {
      type: Array,
      default: () => []
    },
    type: {
      type: String,
      default: 'CV' // CV, LSV, SWV等
    },
    width: {
      type: String,
      default: '100%'
    },
    height: {
      type: String,
      default: '400px'
    },
    title: {
      type: String,
      default: ''
    },
    realTime: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      chart: null
    }
  },
  mounted() {
    this.initChart()
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.dispose()
    }
  },
  watch: {
    data: {
      handler(newData) {
        this.updateChart(newData)
      },
      deep: true
    }
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$refs.chartDom)
      this.updateChart(this.data)
      
      // 自适应窗口大小
      window.addEventListener('resize', () => {
        this.chart.resize()
      })
    },
    
    updateChart(data) {
      if (!this.chart || !data.length) return
      
      const option = this.getChartOption(data)
      
      if (this.realTime) {
        // 实时更新模式
        this.chart.setOption(option, false)
      } else {
        // 静态数据模式
        this.chart.setOption(option, true)
      }
    },
    
    getChartOption(data) {
      const baseOption = {
        title: {
          text: this.title || `${this.type} 曲线`,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const point = params[0]
            return `电压: ${point.value[0].toFixed(3)}V<br/>电流: ${point.value[1].toFixed(6)}A`
          }
        },
        legend: {
          data: ['实验数据'],
          top: 30
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        toolbox: {
          feature: {
            saveAsImage: {},
            dataZoom: {
              yAxisIndex: 'none'
            },
            restore: {}
          }
        },
        xAxis: {
          type: 'value',
          name: '电压 (V)',
          nameLocation: 'middle',
          nameGap: 30,
          axisLabel: {
            formatter: '{value} V'
          }
        },
        yAxis: {
          type: 'value',
          name: '电流 (A)',
          nameLocation: 'middle',
          nameGap: 50,
          axisLabel: {
            formatter: (value) => {
              if (Math.abs(value) >= 1e-3) {
                return `${(value * 1000).toFixed(2)} mA`
              } else if (Math.abs(value) >= 1e-6) {
                return `${(value * 1000000).toFixed(2)} μA`
              } else {
                return `${(value * 1000000000).toFixed(2)} nA`
              }
            }
          }
        },
        dataZoom: [
          {
            type: 'inside',
            xAxisIndex: 0,
            filterMode: 'none'
          },
          {
            type: 'inside',
            yAxisIndex: 0,
            filterMode: 'none'
          }
        ],
        series: [
          {
            name: '实验数据',
            type: 'line',
            data: data.map(point => [point.voltage, point.current]),
            symbol: 'none',
            lineStyle: {
              width: 2,
              color: '#1890ff'
            },
            animation: this.realTime
          }
        ]
      }
      
      // 根据实验类型调整图表配置
      switch (this.type) {
        case 'CV':
          baseOption.xAxis.name = '电压 (V)'
          baseOption.yAxis.name = '电流 (A)'
          break
        case 'LSV':
          baseOption.xAxis.name = '电压 (V)'
          baseOption.yAxis.name = '电流 (A)'
          break
        case 'SWV':
          baseOption.xAxis.name = '电压 (V)'
          baseOption.yAxis.name = '电流 (A)'
          break
        default:
          break
      }
      
      return baseOption
    },
    
    exportChart() {
      if (!this.chart) return
      
      const url = this.chart.getDataURL({
        pixelRatio: 2,
        backgroundColor: '#fff'
      })
      
      const a = document.createElement('a')
      a.href = url
      a.download = `${this.type}_chart_${new Date().toISOString().split('T')[0]}.png`
      a.click()
    },
    
    clearChart() {
      if (this.chart) {
        this.chart.clear()
      }
    }
  }
}
</script>

<style scoped>
.chart-container {
  position: relative;
}

.chart {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
