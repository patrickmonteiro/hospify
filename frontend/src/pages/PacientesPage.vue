<template>
  <div class="q-pa-md">
    <!-- Seção de Upload -->
    <q-card class="q-mb-md">
      <q-card-section>
        <div class="text-h6 q-mb-md">Importar Pacientes</div>
        <div class="row q-gutter-md items-end">
          <div class="col-md-6 col-12">
            <q-file
              v-model="file"
              label="Selecionar arquivo XML"
              accept=".xml"
              @rejected="onRejected"
              outlined
              :disable="uploading"
            >
              <template v-slot:prepend>
                <q-icon name="attach_file" />
              </template>
            </q-file>
          </div>
          <div class="col-auto">
            <q-btn
              label="Importar"
              color="primary"
              @click="uploadFile"
              :loading="uploading"
              :disable="!file || uploading"
              icon="cloud_upload"
            />
          </div>
          <div class="col-auto">
            <q-btn
              label="Limpar"
              color="grey"
              outline
              @click="clearFile"
              :disable="uploading"
              icon="clear"
            />
          </div>
        </div>
      </q-card-section>
    </q-card>

    <!-- Tabela de Pacientes -->
    <q-table
      title="Pacientes"
      :rows="data"
      :columns="columns"
      row-key="id"
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
import { ref, onMounted, onUnmounted } from 'vue'
import { api } from 'boot/axios'
import { useQuasar } from 'quasar'

const $q = useQuasar()

// Variáveis da tabela
const columns = [
  { name: 'id', label: 'ID', field: 'id', align: 'left' },
  { name: 'nome', label: 'Nome', field: 'nome', align: 'left' },
  { name: 'cpf', label: 'CPF', field: 'cpf', align: 'left' },
  { name: 'data_nascimento', label: 'Data Nascimento', field: 'data_nascimento', align: 'left' },
  { name: 'sexo', label: 'Sexo', field: 'sexo', align: 'left' },
  { name: 'telefone', label: 'Telefone', field: 'telefone', align: 'left' },
  { name: 'email', label: 'Email', field: 'email', align: 'left' }
]

const filter = ref('')
const data = ref([])
const loading = ref(false)
const initialPagination = ref({
  sortBy: 'nome',
  descending: false,
  page: 1,
  rowsPerPage: 10
})

// Variáveis do upload
const file = ref(null)
const uploading = ref(false)

// Variável para controlar o polling
let pollingInterval = null

async function getPacientes(showLoading = true) {
  if (showLoading) {
    loading.value = true
  }
  try {
    const res = await api.get('/pacientes')
    console.log(res.data)
    data.value = res.data
  } catch (error) {
    console.error('Erro ao carregar pacientes:', error)
    if (showLoading) {
      $q.notify({
        type: 'negative',
        message: 'Erro ao carregar dados dos pacientes'
      })
    }
  } finally {
    if (showLoading) {
      loading.value = false
    }
  }
}

function startPolling() {
  pollingInterval = setInterval(() => {
    getPacientes(false) // false para não mostrar loading no polling
  }, 20000) // 20 segundos
}

function stopPolling() {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
}

function clearFile() {
  file.value = null
}

function onRejected(rejectedEntries) {
  $q.notify({
    type: 'negative',
    message: `${rejectedEntries.length} arquivo(s) rejeitado(s). Verifique o tamanho e formato.`
  })
}

async function uploadFile() {
  if (!file.value) {
    $q.notify({
      type: 'negative',
      message: 'Selecione um arquivo XML'
    })
    return
  }

  uploading.value = true

  try {
    await api.post('/pacientes/stream', file.value, {
      headers: {
        'Content-Type': 'application/xml'
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        $q.notify({
          type: 'ongoing',
          message: `Enviando arquivo... ${percentCompleted}%`,
          timeout: 0,
          group: 'upload-progress'
        })
      }
    })

    $q.notify({
      type: 'positive',
      message: 'Importação concluída com sucesso!',
      group: 'upload-progress'
    })

    clearFile()
    getPacientes() // Atualiza imediatamente após upload

  } catch (error) {
    console.error('Erro no upload:', error)

    const errorMessage = error.response?.data?.detail ||
                        error.response?.data?.message ||
                        'Erro ao importar arquivo'

    $q.notify({
      type: 'negative',
      message: errorMessage,
      group: 'upload-progress'
    })
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  getPacientes()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>