<template>
    <div class="q-pa-md">
      <q-table
        title="Estados"
        :rows="rows"
        :columns="columns"
        row-key="name"
      />
    </div>
</template>

<script setup>

const columns = [
  { name: 'codigo_uf', label: 'Código', field: 'codigo_uf', align: 'left' },
  { name: 'uf', label: 'UF', field: 'uf', align: 'left' },
  { name: 'nome', label: 'Nome', field: 'latitude', align: 'left' },
  { name: 'latitude', label: 'Latitude', field: 'latitude', align: 'left' },
  { name: 'longitude', label: 'Longitude', field: 'longitude', align: 'left' },
  { name: 'regiao', label: 'Região', field: 'regiao', align: 'left' },
]

const rows = [
  {
    codigo_uf: '12',
    uf: 'SC',
    nome: 'Santa Catarina',
    longitude: 50.10,
    latitude: 80.20,
    regiao: 'Sudeste'
  },
]
</script>