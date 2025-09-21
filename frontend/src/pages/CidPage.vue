<template>
    <div class="q-pa-md">
      <q-table
        title="CID-10"
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
  { name: 'codigo', label: 'codigo', field: 'codigo', align: 'left', classes: 'text-bold' },
  { name: 'descricao', label: 'descricao', field: 'descricao', align: 'left', classes: 'text-bold' },
]
const filter = ref('')
const data = ref([])
const loading = ref(false)
const initialPagination = ref({
  sortBy: 'desc',
  descending: false,
  page: 1,
  rowsPerPage: 10
})


async function getEstados () {
  loading.value = true
  try {
    const res = await api.get('/cid10', {
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