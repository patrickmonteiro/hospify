from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware
# imports chunks 
import os
import uuid
from typing import Dict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from aiofiles import open as aio_open

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:9000", "https://hospify-premier.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "premiersoft"
DB_USER = "postgres"
DB_PASS = "JeFfSc123"

def get_db_connection():
    """Função auxiliar para criar e retornar uma conexão com o banco."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            cursor_factory=RealDictCursor
        )
        return conn
    except psycopg2.OperationalError as e:
        # Se não conseguir conectar, lança um erro HTTP 500
        raise HTTPException(status_code=500, detail=f"Erro ao conectar ao banco de dados: {e}")


# GET endpoints

@app.get("/estados")
def read_estados():
    # Endpoint para buscar e retornar todos os estados cadastrados no banco de dados.
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Executa a query para selecionar todos os dados da tabela estados
        cur.execute("SELECT id, codigo_uf, uf, nome, latitude, longitude, regiao FROM estados ORDER BY nome;")

        # Busca todos os resultados da query.
        estados = cur.fetchall()

        cur.close()

        return estados

    except Exception as e:
        # Captura outros erros que possam ocorrer durante a execução
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {e}")
    finally:
        # Garante que a conexão com o banco seja sempre fechada
        if conn is not None:
            conn.close()

@app.get("/municipios")
def read_estados():
    # Endpoint para buscar e retornar todos os estados cadastrados no banco de dados.
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Executa a query para selecionar todos os dados da tabela estados
        cur.execute("SELECT id, codigo_ibge, nome, latitude, longitude, codigo_uf FROM municipios ORDER BY nome;")

        # Busca todos os resultados da query.
        municipios = cur.fetchall()

        cur.close()

        return municipios

    except Exception as e:
        # Captura outros erros que possam ocorrer durante a execução
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {e}")
    finally:
        # Garante que a conexão com o banco seja sempre fechada
        if conn is not None:
            conn.close()

@app.get("/hospitais")
def read_hospitais():
    # Endpoint para buscar e retornar todos os hospitais cadastrados no banco de dados.
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        sql_query_com_join = """
                SELECT
                h.id,
                h.nome AS nome_hospital,
                h.bairro,
                h.especialidades,
                h.leitos_totais,
                h.codigo_ibge,
                m.nome AS municipio,
                e.nome AS estado
                FROM
                    hospitais AS h
                JOIN
                    municipios AS m ON h.codigo_ibge = m.codigo_ibge
                JOIN
                    estados AS e ON m.codigo_uf = e.codigo_uf 
                ORDER BY
                    h.nome;
        """

        cur.execute(sql_query_com_join)

        # Busca todos os resultados da query.
        municipios = cur.fetchall()

        cur.close()

        return municipios

    except Exception as e:
        # Captura outros erros que possam ocorrer durante a execução
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {e}")
    finally:
        # Garante que a conexão com o banco seja sempre fechada
        if conn is not None:
            conn.close()

@app.get("/medicos")
def read_medicos():
    # Endpoint para buscar e retornar todos os medicos cadastrados no banco de dados.
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Executa a query para selecionar todos os dados da tabela estados
        cur.execute("SELECT id, nome_completo, especialidade, codigo_ibge FROM medicos ORDER BY nome_completo;")

        # Busca todos os resultados da query.
        estados = cur.fetchall()

        cur.close()

        return estados

    except Exception as e:
        # Captura outros erros que possam ocorrer durante a execução
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {e}")
    finally:
        # Garante que a conexão com o banco seja sempre fechada
        if conn is not None:
            conn.close()


@app.get("/pacientes")
def read_pacientes():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Executa a query para selecionar todos os dados da tabela estados
        cur.execute("SELECT id, cpf, nome_completo, genero, codigo_ibge, bairro, convenio, cid10 FROM pacientes ORDER BY nome_completo;")

        # Busca todos os resultados da query.
        pacientes = cur.fetchall()

        cur.close()

        return pacientes

    except Exception as e:
        # Captura outros erros que possam ocorrer durante a execução
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {e}")
    finally:
        # Garante que a conexão com o banco seja sempre fechada
        if conn is not None:
            conn.close()

@app.get("/cid10")
def read_cid10():
    return {"Hello": "World"}

# POST endpoints

@app.post("/municipios")
def create_municipio():
    return {"Hello": "World"}

@app.post("/estados")
def create_estado():
    return {"Hello": "World"}

@app.post("/pacientes")
def create_paciente():
    return {"Hello": "World "}

@app.post("/medicos")
def create_medico():
    return {"Hello": "World"}

@app.post("/cid10")
def create_cid10():
    return {"Hello": "World"}

UPLOAD_STATE: Dict[str, Dict] = {}

@app.post("/upload")
async def upload_chunk(
    file: UploadFile = File(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    filename: str = Form(...),
    upload_id: str = Form(None),
):
    """
    Endpoint para receber as fatias de um arquivo e processá-las em streaming.
    """
    # Se for o primeiro chunk, crie um ID de upload único e inicialize o estado
    if upload_id is None:
        upload_id = str(uuid.uuid4())
        UPLOAD_STATE[upload_id] = {
            "filename": filename,
            "processed_chunks": 0,
            "total_lines": 0,
            "python_occurrences": 0,
        }
        print(f"Novo upload iniciado com ID: {upload_id}")

    # Lida com casos onde o ID de upload não é válido
    if upload_id not in UPLOAD_STATE:
        raise HTTPException(status_code=400, detail="ID de upload inválido.")

    # Processa o conteúdo da fatia de forma assíncrona
    content = await file.read()
    process_chunk(upload_id, content)
    print(content)

    # Aumenta a contagem de fatias processadas
    UPLOAD_STATE[upload_id]["processed_chunks"] += 1
    
    print(f"Fatia {chunk_index}/{total_chunks} de '{filename}' processada.")
    
    # Se esta for a última fatia, finalize o processamento
    if chunk_index == total_chunks - 1:
        final_state = UPLOAD_STATE.pop(upload_id)
        print("Arquivo completamente processado. Limpando o estado.")
        return {
            "message": "Upload e processamento concluídos!",
            "filename": final_state["filename"],
            "total_lines": final_state["total_lines"],
            "python_occurrences": final_state["python_occurrences"],
        }

    return {"message": "Fatia recebida e processada com sucesso!", "upload_id": upload_id}


def process_chunk(upload_id: str, content: bytes):
    """
    Função para processar cada fatia de dados de forma incremental.
    """
    state = UPLOAD_STATE[upload_id]
    
    # Decodifica o conteúdo da fatia para string
    text_content = content.decode("utf-8", errors="ignore")
    lines = text_content.splitlines()

    # Atualiza as contagens no estado do upload
    state["total_lines"] += len(lines)
    state["python_occurrences"] += text_content.lower().count("python")