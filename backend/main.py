import os
import json
import asyncio
import math
from decimal import Decimal
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import xml.etree.ElementTree as ET
import asyncpg
from contextlib import asynccontextmanager
import logging
import uuid

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

# Dicionário em memória para guardar o status das tarefas de alocação
task_status_storage = {}

async def wait_for_db():
    """Aguarda o banco estar disponível com retry"""
    max_retries = 30
    retry_delay = 2
    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1}/{max_retries} de conectar ao banco...")
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    logger.info("Aguardando banco de dados ficar disponível...")
    try:
        await wait_for_db()
        logger.info("Criando pool de conexões...")
        db_pool = await asyncpg.create_pool(**DB_CONFIG)

        logger.info("Verificando/Criando tabelas de alocação...")
        async with db_pool.acquire() as connection:
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS medico_hospital_associacao (
                    id SERIAL PRIMARY KEY,
                    medico_id INTEGER NOT NULL REFERENCES medicos(id) ON DELETE CASCADE,
                    hospital_id INTEGER NOT NULL REFERENCES hospitais(id) ON DELETE CASCADE,
                    distancia_km REAL,
                    UNIQUE (medico_id, hospital_id)
                );
            """)
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS paciente_hospital_alocacao (
                    id SERIAL PRIMARY KEY,
                    paciente_id INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE UNIQUE,
                    hospital_id INTEGER NOT NULL REFERENCES hospitais(id) ON DELETE CASCADE,
                    distancia_km REAL NOT NULL,
                    criterio_especialidade VARCHAR(255)
                );
            """)
        logger.info("Tabelas de alocação prontas.")
        yield
    finally:
        if db_pool:
            logger.info("Fechando conexão com o banco de dados...")
            await db_pool.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", "http://localhost:5173", "https://localhost:5173",
        "http://localhost:9000", "https://localhost:9000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================
# FUNÇÕES AUXILIARES, DE LÓGICA E STREAMING
# =============================================

def json_serial(obj):
    if isinstance(obj, Decimal): return float(obj)
    if isinstance(obj, datetime): return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def haversine(lat1, lon1, lat2, lon2):
    if not all([lat1, lon1, lat2, lon2]): return float('inf')
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

CID10_TO_SPECIALTY_MAP = {
    'A': 'Infectologia', 'B': 'Infectologia', 'C': 'Oncologia', 'D': 'Oncologia',
    'E': 'Endocrinologia', 'F': 'Psiquiatria', 'G': 'Neurologia', 'H': 'Oftalmologia',
    'I': 'Cardiologia', 'J': 'Pneumologia', 'K': 'Gastroenterologia', 'L': 'Dermatologia',
    'M': 'Reumatologia', 'N': 'Nefrologia', 'O': 'Obstetrícia', 'P': 'Pediatria',
    'Q': 'Genética Médica', 'S': 'Ortopedia', 'T': 'Ortopedia'
}

def get_specialty_from_cid10(cid10_code: str):
    if not cid10_code: return 'Clínica Geral'
    return CID10_TO_SPECIALTY_MAP.get(cid10_code[0].upper(), 'Clínica Geral')

async def generate_json_stream(query: str, *args):
    try:
        async with db_pool.acquire() as connection:
            async with connection.transaction():
                cursor = await connection.cursor(query, *args)
                yield '['
                first = True
                while True:
                    record = await cursor.fetchrow()
                    if record is None:
                        break
                    if not first:
                        yield ','
                    yield json.dumps(dict(record), default=json_serial)
                    first = False
                yield ']'
    except Exception as e:
        logger.error(f"Erro durante a geração do stream para a query '{query[:50]}...': {e}")
        yield json.dumps({"error": str(e)})

# =============================================
# LÓGICA DE ALOCAÇÃO EM BACKGROUND
# =============================================

async def executar_logica_alocacao(db_pool: asyncpg.Pool, task_id: str):
    logger.info(f"Iniciando tarefa de alocação ({task_id})...")
    try:
        task_status_storage[task_id] = {"status": "in_progress", "progress": 0, "message": "Buscando dados do banco..."}
        
        async with db_pool.acquire() as connection:
            medicos_db = await connection.fetch("SELECT m.id, m.especialidade, mun.latitude, mun.longitude, mun.codigo_ibge FROM medicos m JOIN municipios mun ON m.codigo_ibge = mun.codigo_ibge;")
            hospitais_db = await connection.fetch("SELECT h.id, h.especialidades, mun.latitude, mun.longitude, mun.codigo_ibge FROM hospitais h JOIN municipios mun ON h.codigo_ibge = mun.codigo_ibge;")
            
            # Alteração para limitar a 1000 pacientes
            pacientes_db = await connection.fetch("""
                SELECT p.id, p.cid10_codigo, mun.latitude, mun.longitude
                FROM pacientes p JOIN municipios mun ON p.codigo_ibge = mun.codigo_ibge
                ORDER BY p.id
                LIMIT 1000;
            """)

            task_status_storage[task_id].update({"progress": 25, "message": f"Processando {len(medicos_db)} médicos..."})
            medico_allocations = []
            for medico in medicos_db:
                hospitais_elegiveis = []
                for hospital in hospitais_db:
                    if medico['especialidade'].lower() in (h.lower() for h in hospital['especialidades']):
                        distancia = haversine(medico['latitude'], medico['longitude'], hospital['latitude'], hospital['longitude'])
                        if distancia <= 30:
                            hospitais_elegiveis.append({"id": hospital['id'], "distancia": distancia, "is_same_city": medico['codigo_ibge'] == hospital['codigo_ibge']})
                
                hospitais_elegiveis.sort(key=lambda x: (not x['is_same_city'], x['distancia']))
                
                for i, h in enumerate(hospitais_elegiveis):
                    if i < 3:
                        medico_allocations.append((medico['id'], h['id'], h['distancia']))

            task_status_storage[task_id].update({"progress": 60, "message": f"Processando {len(pacientes_db)} pacientes..."})
            paciente_allocations = []
            for paciente in pacientes_db:
                especialidade_necessaria = get_specialty_from_cid10(paciente['cid10_codigo'])
                hospitais_compativeis = []
                for hospital in hospitais_db:
                    if especialidade_necessaria.lower() in (h.lower() for h in hospital['especialidades']):
                        distancia = haversine(paciente['latitude'], paciente['longitude'], hospital['latitude'], hospital['longitude'])
                        hospitais_compativeis.append({"id": hospital['id'], "distancia": distancia})
                
                if hospitais_compativeis:
                    melhor_hospital = min(hospitais_compativeis, key=lambda x: x['distancia'])
                    paciente_allocations.append((paciente['id'], melhor_hospital['id'], melhor_hospital['distancia'], especialidade_necessaria))

            task_status_storage[task_id].update({"progress": 90, "message": "Salvando resultados no banco de dados..."})
            async with connection.transaction():
                await connection.execute("TRUNCATE TABLE medico_hospital_associacao, paciente_hospital_alocacao RESTART IDENTITY;")
                if medico_allocations:
                    await connection.copy_records_to_table('medico_hospital_associacao', records=medico_allocations, columns=['medico_id', 'hospital_id', 'distancia_km'])
                if paciente_allocations:
                    await connection.copy_records_to_table('paciente_hospital_alocacao', records=paciente_allocations, columns=['paciente_id', 'hospital_id', 'distancia_km', 'criterio_especialidade'])

        task_status_storage[task_id] = {
            "status": "completed", "progress": 100, "message": "Alocação concluída com sucesso!",
            "details": {"medicos_associados": len(medico_allocations), "pacientes_alocados": len(paciente_allocations)}
        }
        logger.info(f"Tarefa de alocação ({task_id}) concluída.")
    except Exception as e:
        logger.error(f"ERRO na tarefa de alocação ({task_id}): {e}", exc_info=True)
        task_status_storage[task_id] = {"status": "failed", "progress": 0, "message": f"Erro: {str(e)}"}

# =============================================
# ENDPOINTS DA API
# =============================================

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

# --- Endpoints de Alocação ---
@app.post("/alocar", status_code=202)
async def alocar_recursos(background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    task_status_storage[task_id] = {"status": "pending", "progress": 0, "message": "Tarefa agendada."}
    background_tasks.add_task(executar_logica_alocacao, db_pool, task_id)
    return {"message": "Processo de alocação iniciado.", "task_id": task_id, "status_endpoint": f"/alocacao/status/{task_id}"}

@app.get("/alocacao/status/{task_id}")
async def get_alocacao_status(task_id: str):
    status = task_status_storage.get(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    return status

# --- Endpoints de Consulta de Resultados da Alocação ---
@app.get("/medicos/{medico_id}/alocacoes")
async def get_alocacoes_medico(medico_id: int):
    query = """
        SELECT h.id AS hospital_id, h.nome AS nome_hospital, m.nome AS municipio, e.uf, mha.distancia_km
        FROM medico_hospital_associacao mha JOIN hospitais h ON mha.hospital_id = h.id
        JOIN municipios m ON h.codigo_ibge = m.codigo_ibge JOIN estados e ON m.codigo_uf = e.codigo_uf
        WHERE mha.medico_id = $1 ORDER BY mha.distancia_km;
    """
    async with db_pool.acquire() as c: records = await c.fetch(query, medico_id)
    if not records: raise HTTPException(404, "Médico não encontrado ou sem alocações.")
    return [dict(r) for r in records]

@app.get("/pacientes/{paciente_id}/alocacao")
async def get_alocacao_paciente(paciente_id: int):
    query = """
        SELECT h.id AS hospital_id, h.nome, m.nome AS municipio, e.uf, pha.distancia_km, pha.criterio_especialidade
        FROM paciente_hospital_alocacao pha JOIN hospitais h ON pha.hospital_id = h.id
        JOIN municipios m ON h.codigo_ibge = m.codigo_ibge JOIN estados e ON m.codigo_uf = e.codigo_uf
        WHERE pha.paciente_id = $1;
    """
    async with db_pool.acquire() as c: record = await c.fetchrow(query, paciente_id)
    if not record: raise HTTPException(404, "Paciente não encontrado ou não alocado.")
    return dict(record)

# --- Endpoints de Consulta de Dados com Paginação e Streaming ---
@app.get("/estados")
async def stream_estados(offset: int = 0, limit: int = Query(default=100, lte=1000)):
    query = "SELECT id, codigo_uf, uf, nome, latitude, longitude, regiao FROM estados ORDER BY nome LIMIT $1 OFFSET $2;"
    return StreamingResponse(generate_json_stream(query, limit, offset), media_type="application/json")

@app.get("/municipios")
async def stream_municipios(offset: int = 0, limit: int = Query(default=100, lte=1000)):
    query = "SELECT id, codigo_ibge, nome, latitude, longitude, codigo_uf FROM municipios ORDER BY nome LIMIT $1 OFFSET $2;"
    return StreamingResponse(generate_json_stream(query, limit, offset), media_type="application/json")

@app.get("/hospitais")
async def stream_hospitais(offset: int = 0, limit: int = Query(default=100, lte=1000)):
    query = """
        SELECT h.id, h.nome AS nome_hospital, h.bairro, h.especialidades, h.leitos_totais,
            h.codigo_ibge, m.nome AS municipio, e.nome AS estado
        FROM hospitais h JOIN municipios m ON h.codigo_ibge = m.codigo_ibge
        JOIN estados e ON m.codigo_uf = e.codigo_uf
        ORDER BY h.nome LIMIT $1 OFFSET $2;
    """
    return StreamingResponse(generate_json_stream(query, limit, offset), media_type="application/json")

@app.get("/medicos")
async def stream_medicos(offset: int = 0, limit: int = Query(default=100, lte=1000)):
    query = "SELECT id, nome_completo, especialidade, codigo_ibge FROM medicos ORDER BY nome_completo LIMIT $1 OFFSET $2;"
    return StreamingResponse(generate_json_stream(query, limit, offset), media_type="application/json")

@app.get("/pacientes")
async def stream_pacientes_get(offset: int = 0, limit: int = Query(default=100, lte=1000)):
    query = "SELECT id, cpf, nome_completo, genero, codigo_ibge, bairro, convenio, cid10_codigo FROM pacientes ORDER BY nome_completo LIMIT $1 OFFSET $2;"
    return StreamingResponse(generate_json_stream(query, limit, offset), media_type="application/json")

@app.get("/cid10")
async def stream_cid10(offset: int = 0, limit: int = Query(default=100, lte=1000)):
    query = "SELECT codigo, descricao FROM cid10 ORDER BY codigo LIMIT $1 OFFSET $2;"
    return StreamingResponse(generate_json_stream(query, limit, offset), media_type="application/json")

# --- Endpoint de Upload de Pacientes ---
@app.post("/pacientes/stream")
async def stream_pacientes_post(request: Request):
    parser = ET.XMLPullParser(['end'])
    BATCH_SIZE = 5000
    batch = []
    total_pacientes_processados = 0
    upsert_query = """
        INSERT INTO pacientes (cpf, nome_completo, genero, codigo_ibge, bairro, convenio, cid10_codigo)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (cpf) DO UPDATE SET
            nome_completo = EXCLUDED.nome_completo, genero = EXCLUDED.genero,
            codigo_ibge = EXCLUDED.codigo_ibge, bairro = EXCLUDED.bairro,
            convenio = EXCLUDED.convenio, cid10_codigo = EXCLUDED.cid10_codigo;
    """
    try:
        async with db_pool.acquire() as connection:
            async for chunk in request.stream():
                parser.feed(chunk)
                for event, elem in parser.read_events():
                    if elem.tag == 'Paciente':
                        paciente_tuple = (
                            elem.findtext("CPF"), elem.findtext("Nome_Completo"),
                            elem.findtext("Genero"),
                            int(elem.findtext("Cod_municipio")) if elem.findtext("Cod_municipio") else None,
                            elem.findtext("Bairro"), elem.findtext("Convenio"),
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
        logger.error(f"Erro durante o stream de pacientes: {e}")
        raise HTTPException(status_code=500, detail="Ocorreu um erro no processamento do stream.")