import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
import xml.etree.ElementTree as ET
import asyncpg
from contextlib import asynccontextmanager

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Constrói o dicionário de configuração a partir das variáveis de ambiente
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB")
}

db_pool = None

# Gerenciador de ciclo de vida do FastAPI para criar e fechar o pool
@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    print("Conectando ao banco de dados...")
    try:
        db_pool = await asyncpg.create_pool(**DB_CONFIG)
        yield
    finally:
        if db_pool:
            print("Fechando conexão com o banco de dados...")
            await db_pool.close()

app = FastAPI(lifespan=lifespan)

# =============================================
# ENDPOINTS GET (AGORA ASSÍNCRONOS)
# =============================================

@app.get("/estados")
async def read_estados():
    try:
        async with db_pool.acquire() as connection:
            query = "SELECT id, codigo_uf, uf, nome, latitude, longitude, regiao FROM estados ORDER BY nome;"
            estados = await connection.fetch(query)
            return estados
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao buscar estados: {e}")

@app.get("/municipios")
async def read_municipios():
    try:
        async with db_pool.acquire() as connection:
            query = "SELECT id, codigo_ibge, nome, latitude, longitude, codigo_uf FROM municipios ORDER BY nome;"
            municipios = await connection.fetch(query)
            return municipios
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao buscar municípios: {e}")

@app.get("/hospitais")
async def read_hospitais():
    try:
        async with db_pool.acquire() as connection:
            query = """
                SELECT
                    h.id, h.nome AS nome_hospital, h.bairro, h.especialidades, h.leitos_totais,
                    h.codigo_ibge, m.nome AS municipio, e.nome AS estado
                FROM hospitais AS h
                JOIN municipios AS m ON h.codigo_ibge = m.codigo_ibge
                JOIN estados AS e ON m.codigo_uf = e.codigo_uf 
                ORDER BY h.nome;
            """
            hospitais = await connection.fetch(query)
            return hospitais
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao buscar hospitais: {e}")

@app.get("/medicos")
async def read_medicos():
    try:
        async with db_pool.acquire() as connection:
            query = "SELECT id, nome_completo, especialidade, codigo_ibge FROM medicos ORDER BY nome_completo;"
            medicos = await connection.fetch(query)
            return medicos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao buscar médicos: {e}")

@app.get("/pacientes")
async def read_pacientes():
    try:
        async with db_pool.acquire() as connection:
            # CORREÇÃO: Sua query anterior tinha 'cid10, codigo' que parecia um erro de digitação.
            # Assumindo que a coluna se chama 'cid10_codigo'. Ajuste se necessário.
            query = "SELECT id, cpf, nome_completo, genero, codigo_ibge, bairro, convenio, cid10_codigo FROM pacientes ORDER BY nome_completo;"
            pacientes = await connection.fetch(query)
            return pacientes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao buscar pacientes: {e}")

@app.get("/cid10")
async def read_cid10():
    try:
        async with db_pool.acquire() as connection:
            query = "SELECT codigo, descricao FROM cid10 ORDER BY codigo;"
            cid10 = await connection.fetch(query)
            return cid10
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao buscar CID-10: {e}")

# =============================================
# ENDPOINT POST (STREAMING)
# =============================================

@app.post("/pacientes/stream")
async def stream_pacientes(request: Request):
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
        print(f"Erro durante o stream: {e}")
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro no processamento do stream: {e}")