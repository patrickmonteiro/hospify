from fastapi import FastAPI, HTTPException, Request
import psycopg2
from psycopg2.extras import RealDictCursor
import xml.etree.ElementTree as ET
import asyncpg
from contextlib import asynccontextmanager

app = FastAPI()

DB_HOST = "localhost"
DB_PORT = "9000"
DB_NAME = "db"
DB_USER = "admin"
DB_PASS = "admin"

DB_CONFIG = {
    "host": "localhost",
    "port": 9000,
    "user": "admin",
    "password": "admin",
    "database": "db"
}

db_pool = None

# Gerenciador de ciclo de vida do FastAPI para criar e fechar o pool
@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    print("Conectando ao banco de dados...")
    db_pool = await asyncpg.create_pool(**DB_CONFIG)
    yield
    print("Fechando conexão com o banco de dados...")
    await db_pool.close()

app = FastAPI(lifespan=lifespan)

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
def read_municipios():
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
        hospitais = cur.fetchall()

        cur.close()

        return hospitais

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
        medicos = cur.fetchall()

        cur.close()

        return medicos

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
        cur.execute("SELECT id, cpf, nome_completo, genero, codigo_ibge, bairro, convenio, cid10, codigo FROM pacientes ORDER BY nome_completo;")

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
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Executa a query para selecionar todos os dados da tabela estados
        cur.execute("SELECT codigo, descricao FROM cid10 ORDER BY codigo;")

        # Busca todos os resultados da query.
        cid10 = cur.fetchall()

        cur.close()

        return cid10

    except Exception as e:
        # Captura outros erros que possam ocorrer durante a execução
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {e}")
    finally:
        # Garante que a conexão com o banco seja sempre fechada
        if conn is not None:
            conn.close()

# POST endpoints

@app.post("/pacientes")
async def stream_pacientes(request: Request):
    # Verificação do tipo de arquivo (opcional, pode ser feita pelo header Content-Type)
    # content_type = request.headers.get("content-type")
    # if "xml" not in content_type:
    #     raise HTTPException(status_code=400, detail="Apenas arquivos .xml são aceitos.")

    # Inicializa o parser de XML que aceita dados incrementais
    parser = ET.XMLPullParser(['end'])
    
    BATCH_SIZE = 5000  # Lotes menores podem dar um feedback mais rápido no DB
    batch = []
    total_pacientes_processados = 0
    
    # Query de "Inserir ou Atualizar" para asyncpg. Note a sintaxe $1, $2...
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
        # Pega uma conexão do pool
        async with db_pool.acquire() as connection:
            # Itera sobre os "chunks" de bytes que chegam na requisição
            async for chunk in request.stream():
                # Alimenta o parser com o chunk de dados
                parser.feed(chunk)
                
                # Processa os eventos que o parser gerou com o novo chunk
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
                            # A mágica do asyncpg: executemany não bloqueia o servidor
                            await connection.executemany(upsert_query, batch)
                            total_pacientes_processados += len(batch)
                            batch.clear()
                        
                        elem.clear() # Libera a memória do elemento processado

            # Insere o último lote que sobrou
            if batch:
                await connection.executemany(upsert_query, batch)
                total_pacientes_processados += len(batch)
        
        return {"message": f"Stream processado. {total_pacientes_processados} pacientes inseridos/atualizados."}

    except Exception as e:
        # Em caso de erro, é importante logar para saber o que aconteceu
        print(f"Erro durante o stream: {e}")
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro no processamento do stream: {e}")