<template>
  <div class="line-chart">
    <v-chart
      class="chart"
      :option="chartOption"
      :style="{ height: height, width: width }"
    />
  </div>
</template>

<script>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent
])

export default {
  name: 'LineChart',
  components: {
    VChart
  },
  props: {
    data: {
      type: Array,
      default: () => [
        { name: 'Jan', value: 150 },
        { name: 'Feb', value: 230 },
        { name: 'Mar', value: 224 },
        { name: 'Apr', value: 218 },
        { name: 'May', value: 135 },
        { name: 'Jun', value: 147 },
        { name: 'Jul', value: 260 }
      ]
    },
    series: {
      type: Array,
      default: () => []
    },
    title: {
      type: String,
      default: 'Gráfico de Linha'
    },
    height: {
      type: String,
      default: '300px'
    },
    width: {
      type: String,
      default: '100%'
    },
    colors: {
      type: Array,
      default: () => ['#2dd4bf', '#0d9488', '#f39c12', '#2ecc71', '#9b59b6']
    },
    smooth: {
      type: Boolean,
      default: true
    },
    showArea: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    xAxisData() {
      if (this.series.length > 0) {
        return this.series[0].data.map(item => item.name)
      }
      return this.data.map(item => item.name)
    },
    seriesData() {
      if (this.series.length > 0) {
        return this.series.map((serie, index) => ({
          name: serie.name,
          type: 'line',
          smooth: this.smooth,
          data: serie.data.map(item => item.value),
          itemStyle: {
            color: this.colors[index % this.colors.length]
          },
          areaStyle: this.showArea ? {} : null
        }))
      }
      return [{
        name: 'Valores',
        type: 'line',
        smooth: this.smooth,
        data: this.data.map(item => item.value),
        itemStyle: {
          color: this.colors[0]
        },
        areaStyle: this.showArea ? {} : null
      }]
    },
    chartOption() {
      return {
        title: {
          text: this.title,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          }
        },
        legend: {
          data: this.seriesData.map(s => s.name),
          top: 50
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.xAxisData
        },
        yAxis: {
          type: 'value'
        },
        color: this.colors,
        series: this.seriesData
      }
    }
  }
}
</script>

<style scoped>
.line-chart {
  width: 100%;
}

.chart {
  width: 100%;
}
</style>