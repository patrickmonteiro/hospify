<template>
  <div class="bar-chart">
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
import { BarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  BarChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent
])

export default {
  name: 'BarChart',
  components: {
    VChart
  },
  props: {
    data: {
      type: Array,
      default: () => [
        { name: 'Jan', value: 120 },
        { name: 'Feb', value: 200 },
        { name: 'Mar', value: 150 },
        { name: 'Apr', value: 80 },
        { name: 'May', value: 70 },
        { name: 'Jun', value: 110 }
      ]
    },
    title: {
      type: String,
      default: 'Gráfico de Barras'
    },
    height: {
      type: String,
      default: '400px'
    },
    width: {
      type: String,
      default: '100%'
    },
    color: {
      type: String,
      default: '#3498db'
    }
  },
  computed: {
    chartOption() {
      return {
        title: {
          text: this.title,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.data.map(item => item.name),
          axisTick: {
            alignWithLabel: true
          }
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: 'Valores',
            type: 'bar',
            data: this.data.map(item => item.value),
            itemStyle: {
              color: this.color
            }
          }
        ]
      }
    }
  }
}
</script>

<style scoped>
.bar-chart {
  width: 100%;
}

.chart {
  width: 100%;
}
</style>