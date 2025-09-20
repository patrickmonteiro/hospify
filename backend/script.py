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



# --- Suas configurações de DB ---
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "premiersoft"
DB_USER = "postgres"
DB_PASS = "JeFfSc123" # Sua senha

XML_FILE_PATH = "pacientes.xml" # O nome do seu arquivo XML

def importar_xml_pacientes():
    conn = None
    try:
        conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
        cur = conn.cursor()

        tree = ET.parse(XML_FILE_PATH)
        root = tree.getroot() # Pega o elemento raiz <Pacientes>

        print(f"Iniciando a importação do arquivo '{XML_FILE_PATH}'...")

        # Itera sobre cada tag <Paciente>
        for paciente_node in root.findall('Paciente'):
            try:
                cpf = paciente_node.find('CPF').text
                nome = paciente_node.find('Nome_Completo').text
                genero = paciente_node.find('Genero').text
                cod_municipio = paciente_node.find('Cod_municipio').text
                bairro = paciente_node.find('Bairro').text
                convenio = paciente_node.find('Convenio').text
                cid10 = paciente_node.find('CID-10').text # A busca funciona mesmo com o hífen

                # Monta e executa o comando INSERT
                sql_insert = """
                    INSERT INTO pacientes 
                    (cpf, nome_completo, genero, codigo_ibge, bairro, convenio, cid10)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (cpf) DO NOTHING; -- Não faz nada se um paciente com o mesmo CPF já existir
                """
                dados_para_inserir = (cpf, nome, genero, cod_municipio, bairro, convenio, cid10)
                
                cur.execute(sql_insert, dados_para_inserir)

            except AttributeError as e:
                print(f"AVISO: Registro de paciente incompleto no XML. Pulando. Erro: {e}")
                continue

        conn.commit()
        print("✅ Importação de pacientes concluída com sucesso!")

    except FileNotFoundError:
        print(f"ERRO: O arquivo '{XML_FILE_PATH}' não foi encontrado.")
    except psycopg2.Error as e:
        print(f"ERRO de banco de dados: {e}")
        if conn:
            conn.rollback()
    except ET.ParseError as e:
        print(f"ERRO: O arquivo XML está mal formatado. {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            print("Conexão com o banco de dados fechada.")

# Para executar o script
if __name__ == "__main__":
    importar_xml_pacientes()
