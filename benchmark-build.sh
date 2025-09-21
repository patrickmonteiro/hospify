#!/bin/bash

# Script para fazer benchmark do build do frontend
# Uso: ./benchmark-build.sh

echo "🏗️  Benchmark de Build do Frontend"
echo "=================================="

# Função para medir tempo
measure_time() {
    start_time=$(date +%s)
    "$@"
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    echo "⏱️  Tempo de execução: ${duration}s"
}

# Função para mostrar tamanho dos arquivos
show_build_size() {
    if [ -d "frontend/dist" ]; then
        echo "📦 Tamanho do build:"
        du -sh frontend/dist/spa
        echo ""
        echo "📊 Breakdown por tipo de arquivo:"
        find frontend/dist/spa -name "*.js" -exec du -ch {} + | tail -1 | sed 's/\t/ - JS: /'
        find frontend/dist/spa -name "*.css" -exec du -ch {} + | tail -1 | sed 's/\t/ - CSS: /'
        find frontend/dist/spa -name "*.html" -exec du -ch {} + | tail -1 | sed 's/\t/ - HTML: /'

        echo ""
        echo "🗂️  Arquivos principais:"
        find frontend/dist/spa -name "*.js" -type f -exec ls -lh {} \; | head -5
    else
        echo "❌ Build não encontrado"
    fi
}

# Fazer backup do Dockerfile atual
if [ -f "frontend/Dockerfile.backup" ]; then
    echo "📂 Backup do Dockerfile já existe"
else
    echo "💾 Fazendo backup do Dockerfile atual..."
    cp frontend/Dockerfile frontend/Dockerfile.backup
fi

echo ""
echo "1️⃣  Testando build com Docker atual..."
echo "======================================="

# Limpar build anterior
rm -rf frontend/dist

# Medir tempo do build com Docker
echo "🐳 Construindo imagem Docker..."
measure_time docker-compose build frontend

echo ""
echo "2️⃣  Analisando resultado..."
echo "==========================="

# Mostrar tamanho da imagem
echo "🖼️  Tamanho da imagem Docker:"
docker images hospify-frontend --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# Testar build local para comparação
echo ""
echo "3️⃣  Testando build local (para comparação)..."
echo "=============================================="

cd frontend

# Instalar dependências se necessário
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências..."
    measure_time yarn install --frozen-lockfile --silent
fi

# Build local
echo "🔨 Fazendo build local..."
measure_time yarn build

cd ..

# Mostrar tamanhos
show_build_size

echo ""
echo "4️⃣  Resumo de Otimizações Aplicadas..."
echo "====================================="
echo "✅ Build stage otimizado:"
echo "   - Alpine Linux com @quasar/cli global"
echo "   - Yarn configurado para cache offline"
echo "   - Cópia seletiva de arquivos"
echo "   - Flags de produção e silent"
echo ""
echo "✅ Nginx otimizado:"
echo "   - Brotli compression"
echo "   - Gzip aprimorado"
echo "   - Cache agressivo de assets"
echo "   - Headers de segurança"
echo ""
echo "✅ Quasar otimizado:"
echo "   - Terser minification"
echo "   - Tree shaking"
echo "   - Manual chunk splitting"
echo "   - Console.log removido em produção"
echo ""
echo "✅ .dockerignore otimizado:"
echo "   - Exclui arquivos desnecessários"
echo "   - Reduz contexto de build"

echo ""
echo "🎉 Benchmark concluído!"
echo "======================="
echo ""
echo "💡 Para aplicar as otimizações:"
echo "   docker-compose build frontend"
echo "   docker-compose up -d frontend"