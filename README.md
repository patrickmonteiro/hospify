# 🏥 Hospify

Sistema de gerenciamento de médicos, hospitais e pacientes desenvolvido com arquitetura moderna e escalável.

## 📋 Sobre o Projeto

O Hospify é um sistema completo para gestão hospitalar que permite o gerenciamento eficiente de médicos, hospitais e pacientes através de uma interface web moderna e uma API robusta.

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.x** - Linguagem principal
- **FastAPI** - Framework web moderno e rápido para construção de APIs
- **PostgreSQL 17** - Banco de dados relacional
- **AsyncPG** - Driver assíncrono para PostgreSQL
- **Psycopg2** - Driver síncrono para PostgreSQL
- **Uvicorn** - Servidor ASGI para aplicações Python
- **Python-dotenv** - Gerenciamento de variáveis de ambiente

### Frontend
- **Vue.js 3.5.20** - Framework JavaScript progressivo
- **Quasar Framework 2.16.0** - Framework de UI baseado em Vue.js
- **Vue Router 4.x** - Roteamento para aplicações Vue.js
- **Vue I18n 11.x** - Internacionalização
- **Axios 1.2.1** - Cliente HTTP para requisições API
- **ECharts 6.x** - Biblioteca de gráficos
- **Vue-ECharts 7.x** - Integração do ECharts com Vue.js

### DevOps e Infraestrutura
- **Docker & Docker Compose** - Containerização e orquestração
- **Nginx** - Servidor web (em produção)
- **Vite** - Build tool e dev server
- **ESLint** - Linting para JavaScript/Vue
- **Prettier** - Formatação de código

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Docker
- Docker Compose

### Execução Rápida

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd hospify
```

2. **Configure as variáveis de ambiente:**
```bash
cp .envExample .env
# Edite o arquivo .env conforme necessário
```

3. **Inicie o projeto:**
```bash
./docker-utils.sh start
```

### Comandos Disponíveis

O projeto inclui scripts utilitários para facilitar o desenvolvimento:

```bash
# Comandos básicos
./docker-utils.sh start      # Inicia todos os serviços
./docker-utils.sh stop       # Para todos os serviços
./docker-utils.sh restart    # Reinicia todos os serviços
./docker-utils.sh status     # Mostra status dos containers

# Logs e monitoramento
./docker-utils.sh logs           # Logs de todos os serviços
./docker-utils.sh logs backend   # Logs apenas do backend
./docker-utils.sh logs frontend  # Logs apenas do frontend

# Limpeza e manutenção
./docker-utils.sh clean      # Limpeza básica
./docker-utils.sh reset      # Reset completo do projeto
./docker-utils.sh rebuild    # Reconstrói tudo do zero

# Monitoramento específico
./docker-utils.sh import     # Status da importação de dados
```

### Outros Scripts Úteis

```bash
# Reset específico do projeto
./reset-project.sh

# Limpeza profunda do Docker
./docker-cleanup.sh

# Benchmark de build
./benchmark-build.sh
```

## 🌐 Acesso aos Serviços

Após iniciar o projeto, os serviços estarão disponíveis em:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Documentação da API:** http://localhost:8000/docs
- **PostgreSQL:** localhost:9000

## 📁 Estrutura do Projeto

```
hospify/
├── backend/                 # API Python com FastAPI
│   ├── main.py             # Arquivo principal da API
│   ├── requirements.txt    # Dependências Python
│   └── Dockerfile          # Container do backend
├── frontend/               # Aplicação Vue.js com Quasar
│   ├── src/               # Código fonte do frontend
│   ├── package.json       # Dependências Node.js
│   └── Dockerfile         # Container do frontend
├── postgres/              # Scripts de inicialização do PostgreSQL
├── data/                  # Dados para importação
├── docker-compose.yml     # Orquestração dos containers
├── docker-utils.sh        # Script utilitário principal
└── .env                   # Variáveis de ambiente
```

## ⚙️ Configuração

### Variáveis de Ambiente

O arquivo `.env` contém as seguintes configurações:

```env
# Configurações do Banco de Dados PostgreSQL
POSTGRES_DB=hospify
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

### Desenvolvimento

Para desenvolvimento local sem Docker:

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🛡️ Recursos de Segurança

- CORS configurado adequadamente
- Variáveis de ambiente para configurações sensíveis
- Healthchecks configurados para todos os serviços
- Volumes persistentes para dados do PostgreSQL

## 🔧 Scripts de Manutenção

O projeto inclui diversos scripts para facilitar a manutenção:

- **Limpeza automática:** Scripts para limpar containers, imagens e volumes não utilizados
- **Reset completo:** Possibilidade de resetar todo o ambiente rapidamente
- **Benchmarks:** Scripts para medir performance de build
- **Monitoramento:** Verificação de status dos serviços

## 👥 Equipe

- **Patrick Monteiro** - Desenvolvedor Principal
- **Jefferson Caires** - Desenvolvedor
- **Christian Diego** - Desenvolvedor

## 📝 Licença

Este projeto está licenciado sob a licença especificada no arquivo LICENSE.

---

Para mais informações sobre scripts Docker específicos, consulte o arquivo [DOCKER-SCRIPTS.md](DOCKER-SCRIPTS.md).