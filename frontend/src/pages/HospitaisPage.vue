<template>
    <div class="q-pa-md">
      <q-table
        title="Hospitais"
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
  { name: 'bairro', label: 'Bairro', field: 'bairro', align: 'left' },
  { name: 'codigo_ibge', label: 'codigo_ibge', field: 'codigo_ibge', align: 'left' },
  { name: 'especialidades', label: 'especialidades', field: 'especialidades', align: 'left', classes: 'text-bold' },
  { name: 'estado', label: 'estado', field: 'estado', align: 'left', classes: 'text-bold' },
  { name: 'id', label: 'id', field: 'id', align: 'left', classes: 'text-bold' },
  { name: 'leitos_totais', label: 'leitos_totais', field: 'leitos_totais', align: 'left', classes: 'text-bold' },
  { name: 'municipio', label: 'municipio', field: 'municipio', align: 'left', classes: 'text-bold' },
  { name: 'nome_hospital', label: 'nome_hospital', field: 'nome_hospital', align: 'left', classes: 'text-bold' },
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
    const res = await api.get('/hospitais')
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