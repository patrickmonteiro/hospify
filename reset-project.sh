#!/bin/bash

# Script específico para resetar o projeto Hospify
# Uso: ./reset-project.sh

echo "🏥 Resetando projeto Hospify..."
echo "==============================="

# Parar containers do projeto
echo "1️⃣  Parando containers do Hospify..."
docker-compose down -v

# Remover imagens específicas do projeto
echo "2️⃣  Removendo imagens do projeto..."
docker rmi hospify-backend hospify-frontend 2>/dev/null || echo "ℹ️  Imagens do projeto já removidas"

# Remover volume específico do PostgreSQL
echo "3️⃣  Removendo volume do PostgreSQL..."
docker volume rm hospify_postgres_data 2>/dev/null || echo "ℹ️  Volume do PostgreSQL já removido"

# Remover network do projeto
echo "4️⃣  Removendo network do projeto..."
docker network rm hospify_saude_net 2>/dev/null || echo "ℹ️  Network do projeto já removida"

# Limpeza geral (opcional)
echo "5️⃣  Executando limpeza geral..."
docker system prune -f

echo ""
echo "✅ Reset do projeto concluído!"
echo "=============================="
echo ""
echo "🚀 Para reiniciar o projeto:"
echo "   docker-compose up -d"
echo ""
echo "📊 Para monitorar o progresso:"
echo "   docker-compose logs -f backend"
echo "   curl http://localhost:8000/import/status"