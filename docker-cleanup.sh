#!/bin/bash

# Script para parar e limpar completamente o Docker
# Uso: ./docker-cleanup.sh

echo "🐳 Iniciando limpeza completa do Docker..."
echo "=========================================="

# Parar todos os containers do projeto
echo "📦 Parando containers do projeto..."
docker-compose down -v 2>/dev/null || echo "⚠️  Nenhum container rodando ou docker-compose.yml não encontrado"

# Parar TODOS os containers em execução (opcional - descomente se necessário)
# echo "🛑 Parando todos os containers..."
# docker stop $(docker ps -q) 2>/dev/null || echo "ℹ️  Nenhum container rodando"

# Remover containers parados
echo "🗑️  Removendo containers parados..."
docker container prune -f

# Remover imagens não utilizadas
echo "🖼️  Removendo imagens não utilizadas..."
docker image prune -a -f

# Remover volumes não utilizados
echo "💾 Removendo volumes não utilizados..."
docker volume prune -f

# Remover networks não utilizadas
echo "🌐 Removendo networks não utilizadas..."
docker network prune -f

# Remover cache de build
echo "🔧 Removendo cache de build..."
docker builder prune -a -f

# Limpeza completa do sistema (remove tudo que não está sendo usado)
echo "🧹 Executando limpeza completa do sistema..."
docker system prune -a -f --volumes

# Mostrar espaço liberado
echo ""
echo "✅ Limpeza concluída!"
echo "==================="

# Mostrar estatísticas de uso de espaço
echo "📊 Uso atual do Docker:"
docker system df

echo ""
echo "🎉 Script executado com sucesso!"
echo ""
echo "💡 Para reiniciar o projeto:"
echo "   docker-compose up -d"