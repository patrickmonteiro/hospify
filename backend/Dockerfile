# Dockerfile

# 1. Use uma imagem base oficial do Python. A versão 'slim' é menor e mais leve.
FROM python:3.11-slim

# 2. Defina o diretório de trabalho dentro do contêiner.
WORKDIR /app

# 3. Copie o arquivo de dependências PRIMEIRO.
#    Isso aproveita o cache do Docker. Se o requirements.txt não mudar,
#    o Docker não reinstalará as dependências a cada build.
COPY requirements.txt .

# 4. Instale as dependências. A flag --no-cache-dir mantém a imagem menor.
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copie o resto do código da sua aplicação para o diretório de trabalho.
COPY . .

# 6. Exponha a porta que a sua aplicação vai usar (definida no uvicorn).
EXPOSE 8000

# 7. Defina o comando para iniciar a aplicação quando o contêiner rodar.
#    O host '0.0.0.0' é essencial para que a aplicação seja acessível de fora do contêiner.
#    Assumindo que seu arquivo se chama 'main.py' e a instância do FastAPI se chama 'app'.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]