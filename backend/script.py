import csv
import psycopg2
import xml.etree.ElementTree as ET

# --- CONFIGURAÇÕES - ALTERE ESTAS INFORMAÇÕES ---
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "premiersoft"
DB_USER = "postgres"
DB_PASS = "JeFfSc123"
# -----------------------------------------------

def importar_para_tabela_estados():
    """
    Função para importar dados do CSV para a tabela 'estados'.
    """
    # SQL AJUSTADO para a sua tabela 'estados'.
    # A ordem das colunas e dos %s deve ser a mesma do seu CSV!
    sql_insert_query = """
        INSERT INTO estados (codigo_uf, uf, nome, latitude, longitude, regiao)
        VALUES (%s, %s, %s, %s, %s, %s);
    """

    conn = None
    try:
        # Conecta ao banco de dados PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()

        # Abre o arquivo CSV para leitura
        with open(CSV_PATH, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader) # Pula o cabeçalho

            print(f"Iniciando a importação do arquivo '{CSV_PATH}' para a tabela '{TABLE_NAME}'...")
            
            # Itera sobre cada linha do arquivo CSV
            for row in csv_reader:
                try:
                    cur.execute(sql_insert_query, tuple(row))
                except psycopg2.Error as e:
                    print(f"ERRO ao inserir a linha {row}: {e}")
                    conn.rollback() # Desfaz a transação da linha com erro

            # Comita (salva) as alterações no banco
            conn.commit()
            print("✅ Importação concluída com sucesso!")

    except FileNotFoundError:
        print(f"ERRO: O arquivo '{CSV_PATH}' não foi encontrado.")
    except psycopg2.Error as e:
        print(f"ERRO de banco de dados: {e}")
    finally:
        # Garante que a conexão seja fechada
        if conn is not None:
            cur.close()
            conn.close()
            print("Conexão com o banco de dados fechada.")

def importar_para_tabela_municipios():
    """
    Função que importa apenas as colunas necessárias de um CSV,
    independentemente da ordem ou de colunas extras no arquivo.
    """
    # 1. Defina as colunas que a sua TABELA precisa, na ordem do INSERT.
    colunas_requeridas = ['codigo_ibge', 'nome', 'latitude', 'longitude', 'codigo_uf']

    # 2. Crie o SQL com base nas colunas requeridas.
    sql_insert_query = f"""
        INSERT INTO municipios ({', '.join(colunas_requeridas)})
        VALUES ({', '.join(['%s'] * len(colunas_requeridas))});
    """

    conn = None
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()

        with open("municipios.csv", mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            # 3. Leia o cabeçalho do CSV e guarde-o
            header_csv = next(csv_reader)

            # 4. Encontre os índices (posições) das colunas requeridas no cabeçalho do CSV
            try:
                indices_das_colunas = [header_csv.index(col) for col in colunas_requeridas]
            except ValueError as e:
                print(f"ERRO: O CSV não contém todas as colunas necessárias. Coluna faltando: {e}")
                return # Interrompe a execução

            print(f"Iniciando a importação do arquivo 'municipios.csv'...")
            
            # Itera sobre cada linha do arquivo CSV
            for row in csv_reader:
                # 5. Crie uma tupla de dados contendo apenas os valores das colunas que queremos, na ordem correta.
                dados_para_inserir = tuple(row[i] for i in indices_das_colunas)
                
                try:
                    cur.execute(sql_insert_query, dados_para_inserir)
                except psycopg2.Error as e:
                    print(f"ERRO ao inserir a linha {dados_para_inserir}: {e}")
                    conn.rollback()

            conn.commit()
            print("✅ Importação concluída com sucesso!")

    except FileNotFoundError:
        print("ERRO: O arquivo 'municipios.csv' não foi encontrado.")
    except psycopg2.Error as e:
        print(f"ERRO de banco de dados: {e}")
    finally:
        if conn is not None:
            cur.close()
            conn.close()
            print("Conexão com o banco de dados fechada.")

def importar_para_tabela_hospitais():
    """
    Função que importa apenas as colunas necessárias de um CSV,
    independentemente da ordem ou de colunas extras no arquivo.
    """
    # 1. Defina as colunas que a sua TABELA precisa, na ordem do INSERT.
    colunas_requeridas = ['nome', 'codigo_ibge', 'bairro', 'especialidades', 'leitos_totais']

    # 2. Crie o SQL com base nas colunas requeridas.
    sql_insert_query = f"""
        INSERT INTO hospitais ({', '.join(colunas_requeridas)})
        VALUES ({', '.join(['%s'] * len(colunas_requeridas))});
    """

    conn = None
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()

        with open("hospitais.csv", mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            # 3. Leia o cabeçalho do CSV e guarde-o
            header_csv = next(csv_reader)

            # 4. Encontre os índices (posições) das colunas requeridas no cabeçalho do CSV
            try:
                indices_das_colunas = [header_csv.index(col) for col in colunas_requeridas]
            except ValueError as e:
                print(f"ERRO: O CSV não contém todas as colunas necessárias. Coluna faltando: {e}")
                return # Interrompe a execução

            print(f"Iniciando a importação do arquivo 'municipios.csv'...")
            
            # Itera sobre cada linha do arquivo CSV
            for row in csv_reader:
                # 5. Crie uma tupla de dados contendo apenas os valores das colunas que queremos, na ordem correta.
                dados_para_inserir = tuple(row[i] for i in indices_das_colunas)
                
                try:
                    cur.execute(sql_insert_query, dados_para_inserir)
                except psycopg2.Error as e:
                    print(f"ERRO ao inserir a linha {dados_para_inserir}: {e}")
                    conn.rollback()

            conn.commit()
            print("✅ Importação concluída com sucesso!")

    except FileNotFoundError:
        print("ERRO: O arquivo 'municipios.csv' não foi encontrado.")
    except psycopg2.Error as e:
        print(f"ERRO de banco de dados: {e}")
    finally:
        if conn is not None:
            cur.close()
            conn.close()
            print("Conexão com o banco de dados fechada.")

def importar_para_tabela_medicos():
    """
    Função que importa apenas as colunas necessárias de um CSV,
    independentemente da ordem ou de colunas extras no arquivo.
    """
    # 1. Defina as colunas que a sua TABELA precisa, na ordem do INSERT.
    colunas_requeridas = ['nome_completo', 'especialidade', 'codigo_ibge']

    # 2. Crie o SQL com base nas colunas requeridas.
    sql_insert_query = f"""
        INSERT INTO medicos ({', '.join(colunas_requeridas)})
        VALUES ({', '.join(['%s'] * len(colunas_requeridas))});
    """

    conn = None
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()

        with open("medicos.csv", mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            # 3. Leia o cabeçalho do CSV e guarde-o
            header_csv = next(csv_reader)

            # 4. Encontre os índices (posições) das colunas requeridas no cabeçalho do CSV
            try:
                indices_das_colunas = [header_csv.index(col) for col in colunas_requeridas]
            except ValueError as e:
                print(f"ERRO: O CSV não contém todas as colunas necessárias. Coluna faltando: {e}")
                return # Interrompe a execução

            print(f"Iniciando a importação do arquivo 'medicos.csv'...")
            
            # Itera sobre cada linha do arquivo CSV
            for row in csv_reader:
                # 5. Crie uma tupla de dados contendo apenas os valores das colunas que queremos, na ordem correta.
                dados_para_inserir = tuple(row[i] for i in indices_das_colunas)
                
                try:
                    cur.execute(sql_insert_query, dados_para_inserir)
                except psycopg2.Error as e:
                    print(f"ERRO ao inserir a linha {dados_para_inserir}: {e}")
                    conn.rollback()

            conn.commit()
            print("✅ Importação concluída com sucesso!")

    except FileNotFoundError:
        print("ERRO: O arquivo 'medicos.csv' não foi encontrado.")
    except psycopg2.Error as e:
        print(f"ERRO de banco de dados: {e}")
    finally:
        if conn is not None:
            cur.close()
            conn.close()
            print("Conexão com o banco de dados fechada.")



import xml.etree.ElementTree as ET
import psycopg2
from psycopg2.extras import execute_values
import time # Para medir o tempo

# --- Suas configurações de DB ---
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "premiersoft"
DB_USER = "postgres"
DB_PASS = "JeFfSc123"

XML_FILE_PATH = "pacientes.xml" # Seu arquivo de 2.6GB
BATCH_SIZE = 1000 # Inserir 1000 registros por vez. Ajuste conforme a memória.

def importar_xml_pacientes_otimizado():
    conn = None
    total_pacientes = 0
    start_time = time.time()
    
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()

        print(f"Iniciando a importação do arquivo gigante '{XML_FILE_PATH}'...")
        
        batch_de_pacientes = []
        # 1. LEITURA EFICIENTE COM iterparse
        # iterparse lê o arquivo aos poucos. O evento 'end' é disparado quando uma tag é fechada.
        context = ET.iterparse(XML_FILE_PATH, events=('end',))
        
        for event, elem in context:
            # Processamos apenas quando a tag </Paciente> é encontrada
            if elem.tag == 'Paciente':
                try:
                    cpf = elem.find('CPF').text
                    nome = elem.find('Nome_Completo').text
                    genero = elem.find('Genero').text
                    cod_municipio = elem.find('Cod_municipio').text
                    bairro = elem.find('Bairro').text
                    convenio = elem.find('Convenio').text
                    cid10 = elem.find('CID-10').text

                    # Adiciona os dados como uma tupla ao nosso lote
                    batch_de_pacientes.append(
                        (cpf, nome, genero, cod_municipio, bairro, convenio, cid10)
                    )
                    
                    total_pacientes += 1

                    # 2. INSERÇÃO EM LOTE
                    if len(batch_de_pacientes) >= BATCH_SIZE:
                        sql_insert = """
                            INSERT INTO pacientes 
                            (cpf, nome_completo, genero, codigo_ibge, bairro, convenio, cid10)
                            VALUES %s
                            ON CONFLICT (cpf) DO NOTHING;
                        """
                        # execute_values é MUITO mais rápido que múltiplos executes
                        execute_values(cur, sql_insert, batch_de_pacientes)
                        conn.commit() # Salva o lote no banco
                        
                        print(f"{total_pacientes} pacientes processados...")
                        batch_de_pacientes.clear() # Limpa o lote para a próxima rodada

                except (AttributeError, TypeError) as e:
                    print(f"AVISO: Registro de paciente mal formatado no XML. Pulando. Erro: {e}")
                
                # 3. LIBERAÇÃO DE MEMÓRIA
                # Essencial para arquivos grandes: limpa o elemento da memória após o uso
                elem.clear()

        # Insere o último lote que sobrou (caso não seja múltiplo de BATCH_SIZE)
        if batch_de_pacientes:
            print("Inserindo lote final...")
            execute_values(cur, sql_insert, batch_de_pacientes)
            conn.commit()

        end_time = time.time()
        print("✅ Importação concluída com sucesso!")
        print(f"Total de pacientes processados: {total_pacientes}")
        print(f"Tempo total: {end_time - start_time:.2f} segundos")

    except (FileNotFoundError, psycopg2.Error, ET.ParseError) as e:
        print(f"ERRO CRÍTICO: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    importar_xml_pacientes_otimizado()
