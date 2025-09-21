<template>
  <q-page padding>
    <div class="row q-col-gutter-md">
      <div class="col-md-4">
        <q-card flat bordered>
          <q-card-section horizontal>
            <q-card-section class="q-pt-xs col"> <div class="text-h5 q-mt-sm q-mb-xs row justify-between items-center">
                <span class="text-bold">Médicos</span> <q-icon name="mdi-doctor" size="3rem" color="secondary" /> </div>
              <div class="text-secondary text-h4">
                100
              </div>
            </q-card-section>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-md-4">
        <q-card flat bordered>
          <q-card-section horizontal>
            <q-card-section class="q-pt-xs col"> <div class="text-h5 q-mt-sm q-mb-xs row justify-between items-center">
                <span class="text-bold">Hospitais</span> <q-icon name="mdi-doctor" size="3rem" color="secondary" /> </div>
              <div class="text-secondary text-h4">
                100
              </div>
            </q-card-section>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-md-4">
        <q-card flat bordered>
          <q-card-section horizontal>
            <q-card-section class="q-pt-xs col"> <div class="text-h5 q-mt-sm q-mb-xs row justify-between items-center">
                <span class="text-bold">Pacientes</span> <q-icon name="mdi-doctor" size="3rem" color="secondary" /> </div>
              <div class="text-secondary text-h4">
                100
              </div>
            </q-card-section>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <div class="row q-col-gutter-md">
      <div class="col-md-4">
        <BarChart 
          :data="[
            {name: 'Jan', value: 100},
            {name: 'Feb', value: 200},
            {name: 'Mar', value: 300},
            {name: 'Abr', value: 400},
          ]"
          title="Meu Gráfico"
          height="300px"
          color="#2dd4bf"
        />
      </div>
      <div class="col-md-4">
        <PieChart 
          :data="[{name: 'Consultas', value: 300}, {name: 
        'Cirurgias', value: 150}]"
          title="Distribuição de Atendimentos"
          :colors="['#2dd4bf', '#0d9488']"
          inner-radius="50%"
          outer-radius="70%"
        />
      </div>
      <div class="col-md-4">
        <LineChart 
          :series="[
            {name: 'Consultas', data: [
              {name: 'Jan', value: 100},
              {name: 'Fev', value: 200},
              {name: 'Marc', value: 100},
            ]
            },
            {name: 'Cirurgias', data: [
              {name: 'Jan', value: 50},
              {name: 'Jan', value: 150},
              {name: 'Jan', value: 250},
            ]}
          ]"
          title="Comparativo"
        />
      </div>

    </div>
  </q-page>
</template>

<script setup>
import BarChart from 'src/components/BarChart.vue';
import PieChart from 'src/components/PieChart.vue';
import LineChart from 'src/components/LineChart.vue';
//
</script>
