import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import xml.etree.ElementTree as ET
import asyncpg
from contextlib import asynccontextmanager

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB")
}

db_pool = None

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

async def generate_json_stream(query: str):
    try:
        async with db_pool.acquire() as connection:
            async with connection.transaction():
                cursor = await connection.cursor(query)
                yield '['
                first = True
                async for record in cursor:
                    if not first:
                        yield ','
                    yield json.dumps(dict(record))
                    first = False
                yield ']'
    except Exception as e:
        print(f"Erro durante a geração do stream para a query '{query[:50]}...': {e}")

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
    query = "SELECT id, cpf, nome_completo, genero, codigo_ibge, bairro, convenio, cid10_codigo FROM pacientes ORDER BY nome_completo;"
    return StreamingResponse(generate_json_stream(query), media_type="application/json")

@app.get("/cid10")
async def stream_cid10():
    query = "SELECT codigo, descricao FROM cid10 ORDER BY codigo;"
    return StreamingResponse(generate_json_stream(query), media_type="application/json")

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
        print(f"Erro durante o stream: {e}")
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro no processamento do stream: {e}")