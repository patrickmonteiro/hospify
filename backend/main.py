from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware

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
            cursor_factory=RealDictCursor  # <-- A MÁGICA ACONTECE AQUI
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
    return {"Hello": "World"}

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