# 🐳 Scripts Docker - Projeto Hospify

Este diretório contém scripts utilitários para facilitar o gerenciamento do Docker no projeto Hospify.

## 📜 Scripts Disponíveis

### 1. `docker-utils.sh` - Utilitário Principal
Script principal com comandos para o dia a dia.

```bash
# Mostrar ajuda
./docker-utils.sh help

# Comandos básicos
./docker-utils.sh start      # Inicia o projeto
./docker-utils.sh stop       # Para o projeto
./docker-utils.sh restart    # Reinicia o projeto
./docker-utils.sh status     # Status dos containers

# Logs
./docker-utils.sh logs           # Logs de todos os serviços
./docker-utils.sh logs backend   # Logs apenas do backend

# Limpeza e manutenção
./docker-utils.sh clean      # Limpeza básica
./docker-utils.sh reset      # Reset completo do projeto
./docker-utils.sh rebuild    # Reconstrói tudo do zero

# Monitoramento
./docker-utils.sh import     # Status da importação de dados
```

### 2. `reset-project.sh` - Reset Específico
Remove apenas os recursos específicos do projeto Hospify.

```bash
./reset-project.sh
```

**O que faz:**
- Para containers do projeto
- Remove imagens `hospify-backend` e `hospify-frontend`
- Remove volume `hospify_postgres_data`
- Remove network `hospify_saude_net`
- Limpeza básica geral

### 3. `docker-cleanup.sh` - Limpeza Completa
Limpeza profunda de todo o sistema Docker.

```bash
./docker-cleanup.sh
```

**O que faz:**
- Para containers do projeto
- Remove containers parados
- Remove imagens não utilizadas
- Remove volumes órfãos
- Remove networks não utilizadas
- Remove cache de build
- Limpeza completa do sistema

## 🚀 Fluxo de Trabalho Recomendado

### Desenvolvimento Diário
```bash
# Iniciar trabalho
./docker-utils.sh start

# Ver logs durante desenvolvimento
./docker-utils.sh logs backend

# Verificar status da importação
./docker-utils.sh import

# Parar ao final do dia
./docker-utils.sh stop
```

### Problemas ou Mudanças
```bash
# Reset rápido do projeto
./docker-utils.sh reset

# Rebuild completo após mudanças no Dockerfile
./docker-utils.sh rebuild

# Limpeza profunda se necessário
./docker-utils.sh deep-clean
```

### Manutenção Semanal
```bash
# Limpeza básica
./docker-utils.sh clean

# Se precisar de mais espaço
./docker-cleanup.sh
```

## 📊 Monitoramento

### URLs de Acesso
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Status Importação**: http://localhost:8000/import/status

### Comandos de Monitoramento
```bash
# Status dos containers
./docker-utils.sh status

# Logs em tempo real
./docker-utils.sh logs

# Status da importação de dados
./docker-utils.sh import

# Uso de espaço Docker
docker system df
```

## ⚠️ Notas Importantes

1. **Backup**: Os scripts removem dados permanentemente. Faça backup se necessário.

2. **Permissões**: Scripts precisam ter permissão de execução:
   ```bash
   chmod +x *.sh
   ```

3. **Dependências**: Requer Docker e Docker Compose instalados.

4. **Desenvolvimento**: Durante desenvolvimento, use `./docker-utils.sh logs backend` para monitorar a importação.

## 🆘 Solução de Problemas

### Container não inicia
```bash
./docker-utils.sh reset
./docker-utils.sh start
```

### Importação lenta
```bash
./docker-utils.sh import  # Verificar progresso
```

### Falta de espaço
```bash
./docker-cleanup.sh  # Libera ~2GB+
```

### Mudanças não aplicadas
```bash
./docker-utils.sh rebuild  # Rebuild completo
```