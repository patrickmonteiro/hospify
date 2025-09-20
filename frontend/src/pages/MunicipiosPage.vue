<template>
    <div class="q-pa-md">
      <q-table
        title="Municípios"
        :rows="data"
        :columns="columns"
        row-key="name"
        :pagination="initialPagination"
        :loading="loading"
        :filter="filter"
      >
        <template v-slot:top-right>
          <q-input dense debounce="300" v-model="filter" placeholder="Buscar">
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
        </template>
      </q-table>
    </div>
</template>

<script setup>
import { onMounted, ref} from 'vue'
import { api } from 'boot/axios'

const columns = [
  { name: 'nome', label: 'Nome', field: 'nome', align: 'left', classes: 'text-bold' },
  { name: 'id', label: 'Id', field: 'id', align: 'left', classes: 'text-bold' },
  { name: 'codigo_ibge', label: 'Código IBGE', field: 'codigo_ibge', align: 'left' },
  { name: 'codigo_uf', label: 'Código UF', field: 'codigo_uf', align: 'left' },
  { name: 'latitude', label: 'Latitude', field: 'latitude', align: 'left' },
  { name: 'longitude', label: 'Longitude', field: 'longitude', align: 'left' },
]
const filter = ref('')
const data = ref([])
const loading = ref(false)
const initialPagination = ref({
  sortBy: 'desc',
  descending: false,
  page: 1,
  rowsPerPage: 10
  // rowsNumber: xx if getting data from a server
})


async function getEstados () {
  loading.value = true
  try {
    const res = await api.get('/municipios', {
      headers: {
        'Access-Control-Allow-Origin': true
      }
    })
    console.log(res.data)
    loading.value = false
    data.value = res.data
  } catch (error) {
    console.error(error)
    loading.value = false
  }
}


onMounted(() => {
  getEstados()
})


</script>