CREATE TABLE IF NOT EXISTS estados (
    id SERIAL PRIMARY KEY,
    codigo_uf CHAR(2) NOT NULL UNIQUE,
    uf CHAR(2) NOT NULL UNIQUE,
    nome VARCHAR(75) NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    regiao VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS municipios (
    id SERIAL PRIMARY KEY,
    codigo_ibge INTEGER NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    codigo_uf CHAR(2) NOT NULL,
    CONSTRAINT fk_estado FOREIGN KEY (codigo_uf) REFERENCES estados(codigo_uf)
);

CREATE TABLE IF NOT EXISTS cid10 (
    codigo VARCHAR(10) PRIMARY KEY,
    descricao TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hospitais (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    bairro VARCHAR(100),
    especialidades TEXT,
    leitos_totais INTEGER,
    codigo_ibge INTEGER NOT NULL,
    CONSTRAINT codigo_ibge_fk FOREIGN KEY (codigo_ibge) REFERENCES municipios(codigo_ibge) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pacientes (
    id SERIAL PRIMARY KEY,
    cpf VARCHAR(11) UNIQUE NOT NULL,
    nome_completo VARCHAR(255) NOT NULL,
    genero CHAR(1),
    codigo_ibge INTEGER NOT NULL,
    bairro VARCHAR(150),
    convenio CHAR(3),
    cid10 VARCHAR(3),
    CONSTRAINT fk_municipio_residencia FOREIGN KEY (codigo_ibge) REFERENCES municipios(codigo_ibge)
);

CREATE TABLE IF NOT EXISTS medicos (
    id SERIAL PRIMARY KEY,
    nome_completo VARCHAR(255) NOT NULL,
    especialidade VARCHAR(100),
    codigo_ibge INTEGER NOT NULL,
    CONSTRAINT fk_municipio_atendimento FOREIGN KEY (codigo_ibge) REFERENCES municipios(codigo_ibge)
);


CREATE TABLE IF NOT EXISTS medico_hospital (
    id_medico INTEGER NOT NULL,
    id_hospital INTEGER NOT NULL,
    PRIMARY KEY (id_medico, id_hospital),
    CONSTRAINT fk_medico FOREIGN KEY (id_medico) REFERENCES medicos(id) ON DELETE CASCADE,
    CONSTRAINT fk_hospital FOREIGN KEY (id_hospital) REFERENCES hospitais(id) ON DELETE CASCADE
);