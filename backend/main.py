import os
import json
import asyncio
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import xml.etree.ElementTree as ET
import asyncpg
from contextlib import asynccontextmanager
import logging

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constrói o dicionário de configuração a partir das variáveis de ambiente
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB")
}

db_pool = None

async def wait_for_db():
    """Aguarda o banco estar disponível com retry"""
    max_retries = 30
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1}/{max_retries} de conectar ao banco...")
            # Tenta criar uma conexão simples primeiro
            conn = await asyncpg.connect(**DB_CONFIG)
            await conn.close()
            logger.info("Banco de dados está disponível!")
            return True
        except Exception as e:
            logger.warning(f"Falha na conexão (tentativa {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Não foi possível conectar ao banco após todas as tentativas")
                raise

# Gerenciador de ciclo de vida do FastAPI para criar e fechar o pool
@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    logger.info("Aguardando banco de dados ficar disponível...")

    try:
        # Aguarda DB estar pronto
        await wait_for_db()

        # Cria pool de conexões
        logger.info("Criando pool de conexões...")
        db_pool = await asyncpg.create_pool(**DB_CONFIG)

        # Iniciar importação em background após conexão
        asyncio.create_task(start_bulk_import())
        yield
    finally:
        if db_pool:
            logger.info("Fechando conexão com o banco de dados...")
            await db_pool.close()

app = FastAPI(lifespan=lifespan)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Frontend produção
        "http://localhost:5173",    # Vite dev server
        "https://localhost:5173",   # Vite dev server HTTPS
        "http://localhost:9000",    # Quasar dev server
        "https://localhost:9000",   # Quasar dev server HTTPS
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================
# FUNÇÃO DE STREAMING RESPONSE
# =============================================

def json_serial(obj):
    """JSON serializer para objetos não serializáveis por padrão"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

async def generate_json_stream(query: str):
    try:
        async with db_pool.acquire() as connection:
            # Use fetch para buscar todos os registros
            records = await connection.fetch(query)
            yield '['
            first = True
            for record in records:
                if not first:
                    yield ','
                yield json.dumps(dict(record), default=json_serial)
                first = False
            yield ']'
    except Exception as e:
        logger.error(f"Erro durante a geração do stream para a query '{query[:50]}...': {e}")

# =============================================
# FUNÇÕES DE IMPORTAÇÃO EM BACKGROUND
# =============================================

async def check_import_status(table_name: str) -> bool:
    """Verifica se a tabela já foi importada"""
    async with db_pool.acquire() as connection:
        result = await connection.fetchval(
            "SELECT imported FROM bulk_import_status WHERE table_name = $1",
            table_name
        )
        return result or False

async def mark_import_complete(table_name: str, total_records: int):
    """Marca a importação como completa"""
    async with db_pool.acquire() as connection:
        await connection.execute(
            """UPDATE bulk_import_status
               SET imported = TRUE, imported_at = NOW(), total_records = $2
               WHERE table_name = $1""",
            table_name, total_records
        )

async def import_bulk_data():
    """Importa dados em massa do arquivo SQL"""
    try:
        # Verificar se já foi importado
        if await check_import_status('estados'):
            logger.info("Dados já foram importados anteriormente")
            return

        logger.info("Iniciando importação de dados em massa...")

        # Ler arquivo SQL
        with open('/app/bulk_data.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()

        async with db_pool.acquire() as connection:
            # Desabilitar constraints temporariamente para inserção em massa
            await connection.execute("SET session_replication_role = replica;")

            # Executar em chunks para evitar timeout
            statements = sql_content.split(';')
            processed = 0
            errors = 0

            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        await connection.execute(statement)
                        processed += 1

                        if processed % 5000 == 0:
                            logger.info(f"Processadas {processed} declarações SQL")
                            await asyncio.sleep(0.1)  # Pequena pausa para não sobrecarregar

                    except Exception as e:
                        errors += 1
                        if errors <= 10:  # Log apenas os primeiros 10 erros
                            logger.warning(f"Erro ao executar statement: {e}")

            # Reabilitar constraints
            await connection.execute("SET session_replication_role = DEFAULT;")

        # Contar registros inseridos por tabela
        async with db_pool.acquire() as connection:
            estados_count = await connection.fetchval("SELECT COUNT(*) FROM estados")
            municipios_count = await connection.fetchval("SELECT COUNT(*) FROM municipios")
            cid10_count = await connection.fetchval("SELECT COUNT(*) FROM cid10")
            hospitais_count = await connection.fetchval("SELECT COUNT(*) FROM hospitais")
            medicos_count = await connection.fetchval("SELECT COUNT(*) FROM medicos")

        # Marcar como importado com contagens reais
        await mark_import_complete('estados', estados_count)
        await mark_import_complete('municipios', municipios_count)
        await mark_import_complete('cid10', cid10_count)
        await mark_import_complete('hospitais', hospitais_count)
        await mark_import_complete('medicos', medicos_count)

        logger.info(f"Importação concluída! {processed} statements processados, {errors} erros ignorados")
        logger.info(f"Registros: {estados_count} estados, {municipios_count} municípios, {cid10_count} CIDs, {hospitais_count} hospitais, {medicos_count} médicos")

    except FileNotFoundError:
        logger.warning("Arquivo bulk_data.sql não encontrado")
    except Exception as e:
        logger.error(f"Erro durante importação: {e}")

async def start_bulk_import():
    """Inicia a importação em background"""
    await asyncio.sleep(5)  # Aguarda 5s para garantir que o DB está pronto
    await import_bulk_data()

# =============================================
# ENDPOINTS DE STATUS E CONTROLE
# =============================================

@app.get("/import/status")
async def get_import_status():
    """Retorna o status da importação"""
    try:
        async with db_pool.acquire() as connection:
            status = await connection.fetch(
                "SELECT table_name, imported, imported_at, total_records FROM bulk_import_status"
            )
            return {"import_status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao verificar status: {e}")

@app.post("/import/trigger")
async def trigger_import(background_tasks: BackgroundTasks):
    """Dispara importação manual"""
    background_tasks.add_task(import_bulk_data)
    return {"message": "Importação iniciada em background"}

# =============================================
# ENDPOINTS GET COM STREAMING RESPONSE
# =============================================

@app.get("/estados")
async def stream_estados():
    query = "SELECT id, codigo_uf, uf, nome, latitude, longitude, regiao FROM estados ORDER BY nome;"
    return StreamingResponse(generate_json_stream(query), media_type="application/json")

@app.get("/municipios")
async def stream_municipios():
    query = "SELECT id, codigo_ibge, nome, latitude, longitude, codigo_uf FROM municipios ORDER BY nome;"
    return StreamingResponse(generate_json_stream(query), media_type="application/json")

@app.get("/hospitais")
async def stream_hospitais():
    query = """
        SELECT
            h.id, h.nome AS nome_hospital, h.bairro, h.especialidades, h.leitos_totais,
            h.codigo_ibge, m.nome AS municipio, e.nome AS estado
        FROM hospitais AS h
        JOIN municipios AS m ON h.codigo_ibge = m.codigo_ibge
        JOIN estados AS e ON m.codigo_uf = e.codigo_uf
        ORDER BY h.nome;
    """
    return StreamingResponse(generate_json_stream(query), media_type="application/json")

@app.get("/medicos")
async def stream_medicos():
    query = "SELECT id, nome_completo, especialidade, codigo_ibge FROM medicos ORDER BY nome_completo;"
    return StreamingResponse(generate_json_stream(query), media_type="application/json")

@app.get("/pacientes")
async def stream_pacientes_get():
    query = "SELECT id, cpf, nome_completo, genero, codigo_ibge, bairro, convenio, cid10_codigo FROM pacientes ORDER BY nome_completo LIMIT 500;"
    return StreamingResponse(generate_json_stream(query), media_type="application/json")

@app.get("/cid10")
async def stream_cid10():
    query = "SELECT codigo, descricao FROM cid10 ORDER BY codigo;"
    return StreamingResponse(generate_json_stream(query), media_type="application/json")

# =============================================
# ENDPOINT POST PARA UPLOAD DE PACIENTES
# =============================================

@app.post("/pacientes/stream")
async def stream_pacientes_post(request: Request):

@app.get("/stats")
async def get_database_stats():
    stats = {}
    tables = ["estados", "municipios", "cid10", "hospitais", "medicos", "pacientes"]
    try:
        async with db_pool.acquire() as connection:
            for table in tables:
                stats[table] = await connection.fetchval(f"SELECT COUNT(*) FROM {table}")
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao obter estatísticas.")
    parser = ET.XMLPullParser(['end'])
    BATCH_SIZE = 5000
    batch = []
    total_pacientes_processados = 0

    upsert_query = """
        INSERT INTO pacientes (cpf, nome_completo, genero, codigo_ibge, bairro, convenio, cid10_codigo)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (cpf) DO UPDATE SET
            nome_completo = EXCLUDED.nome_completo,
            genero = EXCLUDED.genero,
            codigo_ibge = EXCLUDED.codigo_ibge,
            bairro = EXCLUDED.bairro,
            convenio = EXCLUDED.convenio,
            cid10_codigo = EXCLUDED.cid10_codigo;
    """
    try:
        async with db_pool.acquire() as connection:
            async for chunk in request.stream():
                parser.feed(chunk)
                for event, elem in parser.read_events():
                    if elem.tag == 'Paciente':
                        paciente_tuple = (
                            elem.findtext("CPF"),
                            elem.findtext("Nome_Completo"),
                            elem.findtext("Genero"),
                            # Converte para integer, se necessário
                            int(elem.findtext("Cod_municipio")) if elem.findtext("Cod_municipio") else None,
                            elem.findtext("Bairro"),
                            elem.findtext("Convenio"),
                            elem.findtext("CID-10")
                        )
                        batch.append(paciente_tuple)

                        if len(batch) >= BATCH_SIZE:
                            await connection.executemany(upsert_query, batch)
                            total_pacientes_processados += len(batch)
                            batch.clear()

                        elem.clear()

            if batch:
                await connection.executemany(upsert_query, batch)
                total_pacientes_processados += len(batch)

        return {"message": f"Stream processado. {total_pacientes_processados} pacientes inseridos/atualizados."}

    except Exception as e:
        logger.error(f"Erro durante o stream: {e}")
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro no processamento do stream: {e}")