<template>
  <div>
    <input type="file" @change="handleFileUpload" />
    <p v-if="fileName">Arquivo selecionado: {{ fileName }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const file = ref(null);
const fileName = ref('');

const handleFileUpload = (event) => {
  const selectedFile = event.target.files[0];
  if (selectedFile) {
    file.value = selectedFile;
    fileName.value = selectedFile.name;
    console.log('Arquivo selecionado:', file.value);
    // Aqui você pode chamar a função para fatiar e processar o arquivo
    processFile(file.value);
  }
};

const CHUNK_SIZE = 1024 * 1024; // 1MB por fatia, ajuste conforme a necessidade

const processFile = (fileToProcess) => {
  if (!fileToProcess) return;

  const totalChunks = Math.ceil(fileToProcess.size / CHUNK_SIZE);
  console.log(`O arquivo será dividido em ${totalChunks} fatias.`);

  for (let i = 0; i < totalChunks; i++) {
    const start = i * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, fileToProcess.size);
    const chunk = fileToProcess.slice(start, end);

    // Envie a fatia para o servidor
    uploadChunk(chunk, i, totalChunks);
  }
};

const uploadChunk = (chunk, index, total) => {
  const formData = new FormData();
  formData.append('file_chunk', chunk);
  formData.append('chunk_index', index);
  formData.append('total_chunks', total);
  formData.append('file_name', fileName.value); // O nome do arquivo original
  // Use uma biblioteca como Axios ou a Fetch API para enviar
  // a fatia para o seu endpoint de upload no servidor.
  // Exemplo com Fetch API:
  fetch('http://seu-servidor.com/upload', {
    method: 'POST',
    body: formData,
  })
    .then(response => response.json())
    .then(data => {
      console.log(data)
      console.log(`Fatia ${index + 1} de ${total} enviada com sucesso!`);
      // O servidor deve retornar um status para indicar que a fatia foi recebida.
      // Se for a última fatia, o servidor pode processar ou unir o arquivo completo.
    })
    .catch(error => {
      console.error('Erro ao enviar a fatia:', error);
    });
};


</script>
