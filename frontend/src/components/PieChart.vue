<template>
  <div class="donut-chart">
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
import { PieChart } from 'echarts/charts'
import {
  TooltipComponent,
  TitleComponent,
  LegendComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  PieChart,
  TooltipComponent,
  TitleComponent,
  LegendComponent
])

export default {
  name: 'PieChart',
  components: {
    VChart
  },
  props: {
    data: {
      type: Array,
      default: () => [
        { name: 'Consultas', value: 320 },
        { name: 'Cirurgias', value: 240 },
        { name: 'Emergências', value: 149 },
        { name: 'Exames', value: 100 },
        { name: 'Outros', value: 50 }
      ]
    },
    title: {
      type: String,
      default: 'Gráfico Donut'
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
      default: () => ['#3498db', '#e74c3c', '#f39c12', '#2ecc71', '#9b59b6']
    },
    innerRadius: {
      type: String,
      default: '40%'
    },
    outerRadius: {
      type: String,
      default: '70%'
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
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        color: this.colors,
        series: [
          {
            name: 'Dados',
            type: 'pie',
            radius: [this.innerRadius, this.outerRadius],
            center: ['50%', '60%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 20,
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: this.data
          }
        ]
      }
    }
  }
}
</script>

<style scoped>
.donut-chart {
  width: 100%;
}

.chart {
  width: 100%;
}
</style>