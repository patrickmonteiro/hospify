from fastapi import FastAPI, HTTPException, File, UploadFile
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from aiofiles import open as aio_open
import xml.etree.ElementTree as ET

app = FastAPI()


DB_HOST = "localhost"
DB_PORT = "9000"
DB_NAME = "db"
DB_USER = "admin"
DB_PASS = "admin"

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
def create_paciente(file: UploadFile = File(...)):
    if not file.filename.endswith(".xml"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .xml são aceitos.")

    conn = None
    BATCH_SIZE = 10000
    batch = []
    total_pacientes_processados = 0

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        insert_query = """
            INSERT INTO pacientes (
                cpf, nome_completo, genero, codigo_ibge, bairro, convenio, cid10_codigo
            ) VALUES %s;
        """

        context = ET.iterparse(file.file, events=('end',))

        for event, elem in context:
            if elem.tag == 'Paciente':
                paciente_tuple = (
                    elem.findtext("CPF"),
                    elem.findtext("Nome_Completo"),
                    elem.findtext("Genero"),
                    elem.findtext("Cod_municipio"),
                    elem.findtext("Bairro"),
                    elem.findtext("Convenio"),
                    elem.findtext("CID-10")
                )
                batch.append(paciente_tuple)

                if len(batch) >= BATCH_SIZE:
                    execute_values(cur, insert_query, batch)
                    total_pacientes_processados += len(batch)
                    batch.clear()

                elem.clear()

        if batch:
            execute_values(cur, insert_query, batch)
            total_pacientes_processados += len(batch)

        conn.commit()
        cur.close()

        return {"message": f"Total de {total_pacientes_processados} pacientes inseridos com sucesso!"}

    except (Exception, psycopg2.Error) as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro no processamento: {e}")
    finally:
        if conn is not None:
            conn.close()