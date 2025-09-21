#!/bin/bash

# Utilitários Docker para o projeto Hospify
# Uso: ./docker-utils.sh [comando]

function show_help() {
    echo "🏥 Utilitários Docker - Projeto Hospify"
    echo "======================================"
    echo ""
    echo "Comandos disponíveis:"
    echo "  start       - Inicia o projeto"
    echo "  stop        - Para o projeto"
    echo "  restart     - Reinicia o projeto"
    echo "  logs        - Mostra logs de todos os serviços"
    echo "  status      - Mostra status dos containers"
    echo "  clean       - Limpeza básica"
    echo "  reset       - Reset completo do projeto"
    echo "  deep-clean  - Limpeza profunda do Docker"
    echo "  import      - Status da importação de dados"
    echo "  rebuild     - Reconstrói e reinicia tudo"
    echo ""
    echo "Exemplos:"
    echo "  ./docker-utils.sh start"
    echo "  ./docker-utils.sh logs backend"
    echo "  ./docker-utils.sh status"
}

function start_project() {
    echo "🚀 Iniciando projeto..."
    docker-compose up -d
    echo "✅ Projeto iniciado!"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend:  http://localhost:8000"
}

function stop_project() {
    echo "⏸️  Parando projeto..."
    docker-compose down
    echo "✅ Projeto parado!"
}

function restart_project() {
    echo "🔄 Reiniciando projeto..."
    docker-compose restart
    echo "✅ Projeto reiniciado!"
}

function show_logs() {
    if [ -n "$2" ]; then
        echo "📋 Logs do serviço $2..."
        docker-compose logs -f "$2"
    else
        echo "📋 Logs de todos os serviços..."
        docker-compose logs -f
    fi
}

function show_status() {
    echo "📊 Status dos containers:"
    docker-compose ps
    echo ""
    echo "💾 Uso do Docker:"
    docker system df
}

function clean_basic() {
    echo "🧹 Limpeza básica..."
    docker system prune -f
    echo "✅ Limpeza básica concluída!"
}

function reset_project() {
    echo "🔄 Reset completo do projeto..."
    ./reset-project.sh
}

function deep_clean() {
    echo "🧽 Limpeza profunda..."
    ./docker-cleanup.sh
}

function import_status() {
    echo "📊 Status da importação de dados:"
    curl -s http://localhost:8000/import/status | python3 -m json.tool 2>/dev/null || echo "❌ Backend não está respondendo"
}

function rebuild_all() {
    echo "🏗️  Reconstruindo projeto..."
    docker-compose down -v
    docker-compose build --no-cache
    docker-compose up -d
    echo "✅ Projeto reconstruído!"
}

# Processar comando
case "$1" in
    "start")
        start_project
        ;;
    "stop")
        stop_project
        ;;
    "restart")
        restart_project
        ;;
    "logs")
        show_logs "$@"
        ;;
    "status")
        show_status
        ;;
    "clean")
        clean_basic
        ;;
    "reset")
        reset_project
        ;;
    "deep-clean")
        deep_clean
        ;;
    "import")
        import_status
        ;;
    "rebuild")
        rebuild_all
        ;;
    "help"|"--help"|"-h"|"")
        show_help
        ;;
    *)
        echo "❌ Comando não reconhecido: $1"
        echo ""
        show_help
        exit 1
        ;;
esac