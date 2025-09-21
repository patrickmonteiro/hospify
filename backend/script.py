import csv
import time
import psycopg2
import xml.etree.ElementTree as ET
from psycopg2.extras import execute_values

# --- 1. CONFIGURAÇÃO CENTRALIZADA ---
# Mantenha todas as configurações em um único lugar.
DB_CONFIG = {
    "host": "localhost",
    "port": "9000",
    "dbname": "db",
    "user": "admin",
    "password": "admin"
}

BATCH_SIZE = 2000 # Lote de inserção para todos os arquivos

# --- 2. GERENCIADOR DE CONEXÃO COM O BANCO ---
# Esta classe gerencia a conexão, commit, rollback e fechamento automaticamente.
# Isso elimina a repetição do bloco try/except/finally em todas as funções.
class DatabaseManager:
    """Um gerenciador de contexto para conexões com o banco de dados PostgreSQL."""
    def __init__(self, config):
        self.config = config
        self.conn = None
        self.cur = None

    def __enter__(self):
        """Abre a conexão e o cursor ao entrar no bloco 'with'."""
        self.conn = psycopg2.connect(**self.config)
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Fecha a conexão ao sair do bloco 'with'.
        Faz commit se tudo deu certo, ou rollback em caso de erro.
        """
        try:
            if exc_val is not None:  # Se ocorreu um erro
                print(f"Ocorreu um erro, revertendo transação: {exc_val}")
                self.conn.rollback()
            else:
                self.conn.commit()
                print("Transação concluída com sucesso.")
        finally:
            if self.cur:
                self.cur.close()
            if self.conn:
                self.conn.close()
            print("Conexão com o banco de dados fechada.")

# --- 3. FUNÇÕES DE IMPORTAÇÃO ---

def importar_csv_generico(db_config, filepath, table_name, colunas_tabela, colunas_csv_map):
    """
    Função genérica e otimizada para importar QUALQUER arquivo CSV em lotes.

    Args:
        db_config (dict): Dicionário com as credenciais do banco.
        filepath (str): Caminho para o arquivo CSV.
        table_name (str): Nome da tabela de destino.
        colunas_tabela (list): Lista de nomes das colunas na tabela do banco.
        colunas_csv_map (list): Lista dos nomes correspondentes no cabeçalho do CSV.
    """
    print(f"\nIniciando importação de '{filepath}' para a tabela '{table_name}'...")
    start_time = time.time()
    total_rows = 0
    
    try:
        with open(filepath, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            batch = []

            # Usa o gerenciador de conexão
            with DatabaseManager(db_config) as cur:
                for row in reader:
                    # Monta a tupla de dados na ordem correta das colunas da tabela
                    dados_para_inserir = tuple(row[col_csv] for col_csv in colunas_csv_map)
                    batch.append(dados_para_inserir)
                    
                    if len(batch) >= BATCH_SIZE:
                        # Gera o SQL dinamicamente
                        sql = f"INSERT INTO {table_name} ({', '.join(colunas_tabela)}) VALUES %s ON CONFLICT DO NOTHING"
                        execute_values(cur, sql, batch)
                        total_rows += len(batch)
                        print(f"{total_rows} registros de '{table_name}' inseridos...")
                        batch.clear()

                # Insere o lote final
                if batch:
                    sql = f"INSERT INTO {table_name} ({', '.join(colunas_tabela)}) VALUES %s ON CONFLICT DO NOTHING"
                    execute_values(cur, sql, batch)
                    total_rows += len(batch)

    except FileNotFoundError:
        print(f"ERRO: Arquivo '{filepath}' não encontrado.")
        return
    except Exception as e:
        print(f"ERRO CRÍTICO durante a importação de '{filepath}': {e}")
        return

    end_time = time.time()
    print(f"Finalizada a importação de '{table_name}'. Total de {total_rows} registros em {end_time - start_time:.2f} segundos.")


def importar_xml_pacientes(db_config, filepath):
    """
    Função otimizada para importar um arquivo XML de grande volume.
    """
    print(f"\nIniciando importação de XML gigante '{filepath}'...")
    start_time = time.time()
    total_pacientes = 0
    
    try:
        # Usa o gerenciador de conexão
        with DatabaseManager(db_config) as cur:
            batch = []
            context = ET.iterparse(filepath, events=('end',))
            
            for _, elem in context:
                if elem.tag == 'Paciente':
                    # Extração e transformação de dados
                    cpf = elem.find('CPF').text
                    # ... (extraia todos os outros campos como antes)
                    
                    # Monta a tupla
                    dados_paciente = (cpf, ...) # Adicione os outros campos
                    batch.append(dados_paciente)

                    if len(batch) >= BATCH_SIZE:
                        sql = "INSERT INTO pacientes (cpf, ...) VALUES %s ON CONFLICT (cpf) DO NOTHING"
                        execute_values(cur, sql, batch)
                        total_pacientes += len(batch)
                        print(f"{total_pacientes} pacientes inseridos...")
                        batch.clear()
                    
                    elem.clear() # Libera memória

            # Insere o lote final
            if batch:
                sql = "INSERT INTO pacientes (cpf, ...) VALUES %s ON CONFLICT (cpf) DO NOTHING"
                execute_values(cur, sql, batch)
                total_pacientes += len(batch)

    except FileNotFoundError:
        print(f"ERRO: Arquivo '{filepath}' não encontrado.")
        return
    except Exception as e:
        print(f"ERRO CRÍTICO durante a importação do XML: {e}")
        return

    end_time = time.time()
    print(f"Finalizada a importação de pacientes. Total de {total_pacientes} registros em {end_time - start_time:.2f} segundos.")


# --- 4. ORQUESTRADOR PRINCIPAL ---
def main():

    # Importar Estados
    importar_csv_generico(
        db_config=DB_CONFIG,
        filepath="estados.csv",
        table_name="estados",
        colunas_tabela=['codigo_uf', 'uf', 'nome', 'latitude', 'longitude', 'regiao'],
        colunas_csv_map=['codigo_uf', 'uf', 'nome', 'latitude', 'longitude', 'regiao']
    )
    
    # Importar Municípios
    importar_csv_generico(
        db_config=DB_CONFIG,
        filepath="municipios.csv",
        table_name="municipios",
        colunas_tabela=['codigo_ibge', 'nome', 'latitude', 'longitude', 'codigo_uf'],
        colunas_csv_map=['codigo_ibge', 'nome', 'latitude', 'longitude', 'codigo_uf']
    )

    # Importar Hospitais (Exemplo com mapeamento de colunas diferentes)
    importar_csv_generico(
        db_config=DB_CONFIG,
        filepath="hospitais.csv",
        table_name="hospitais",
        colunas_tabela=['nome', 'codigo_ibge', 'bairro'],
        colunas_csv_map=['nome_hospital', 'cidade_ibge', 'bairro_local'] # Nomes hipotéticos no CSV
    )

    # Importar Pacientes do XML Gigante
    # importar_xml_pacientes(db_config=DB_CONFIG, filepath="pacientes.xml")

    print("\n--- PROCESSO DE IMPORTAÇÃO FINALIZADO ---")


if __name__ == "__main__":
    main()