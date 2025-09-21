-- init.sql
-- Script de inicialização do banco de dados.
-- Este script será executado automaticamente na primeira vez que o container do Postgres for iniciado.
-- Versão focada apenas na criação da estrutura (tabelas e índices), sem dados iniciais.

-- Adiciona extensões úteis.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Inicia uma transação. Se qualquer comando falhar, todas as alterações serão desfeitas.
BEGIN;

-- =============================================
-- CRIAÇÃO DAS TABELAS
-- =============================================

-- Tabela de Estados
CREATE TABLE IF NOT EXISTS estados (
    id SERIAL PRIMARY KEY,
    codigo_uf CHAR(2) NOT NULL UNIQUE,
    uf CHAR(2) NOT NULL UNIQUE,
    nome VARCHAR(75) NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    regiao VARCHAR(20) NOT NULL
);

-- Tabela de Municípios
CREATE TABLE IF NOT EXISTS municipios (
    id SERIAL PRIMARY KEY,
    codigo_ibge INTEGER NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    codigo_uf CHAR(2) NOT NULL,
    CONSTRAINT fk_estado FOREIGN KEY (codigo_uf) REFERENCES estados(codigo_uf)
);

-- Tabela CID-10 (Classificação Internacional de Doenças)
CREATE TABLE IF NOT EXISTS cid10 (
    codigo VARCHAR(10) PRIMARY KEY,
    descricao TEXT NOT NULL
);

-- Tabela de Hospitais
CREATE TABLE IF NOT EXISTS hospitais (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    bairro VARCHAR(100),
    especialidades TEXT,
    leitos_totais INTEGER,
    codigo_ibge INTEGER NOT NULL,
    CONSTRAINT fk_municipio FOREIGN KEY (codigo_ibge) REFERENCES municipios(codigo_ibge) ON DELETE CASCADE
);

-- Tabela de Pacientes
CREATE TABLE IF NOT EXISTS pacientes (
    id SERIAL PRIMARY KEY,
    cpf VARCHAR(11) UNIQUE NOT NULL,
    nome_completo VARCHAR(255) NOT NULL,
    genero CHAR(1),
    codigo_ibge INTEGER NOT NULL,
    bairro VARCHAR(150),
    convenio CHAR(3),
    cid10_codigo VARCHAR(10), -- Nome ajustado para clareza
    CONSTRAINT fk_cid10 FOREIGN KEY (cid10_codigo) REFERENCES cid10(codigo)
);

-- Tabela de Médicos
CREATE TABLE IF NOT EXISTS medicos (
    id SERIAL PRIMARY KEY,
    nome_completo VARCHAR(255) NOT NULL,
    especialidade VARCHAR(100),
    codigo_ibge INTEGER NOT NULL,
    CONSTRAINT fk_municipio_atendimento FOREIGN KEY (codigo_ibge) REFERENCES municipios(codigo_ibge)
);

-- Tabela de Associação entre Médicos e Hospitais (Many-to-Many)
CREATE TABLE IF NOT EXISTS medico_hospital (
    id_medico INTEGER NOT NULL,
    id_hospital INTEGER NOT NULL,
    PRIMARY KEY (id_medico, id_hospital),
    CONSTRAINT fk_medico FOREIGN KEY (id_medico) REFERENCES medicos(id) ON DELETE CASCADE,
    CONSTRAINT fk_hospital FOREIGN KEY (id_hospital) REFERENCES hospitais(id) ON DELETE CASCADE
);

-- =============================================
-- CRIAÇÃO DE ÍNDICES PARA PERFORMANCE
-- =============================================
-- Índices em chaves estrangeiras aceleram muito as consultas com JOINs.

CREATE INDEX IF NOT EXISTS idx_municipios_codigo_uf ON municipios(codigo_uf);
CREATE INDEX IF NOT EXISTS idx_hospitais_codigo_ibge ON hospitais(codigo_ibge);
CREATE INDEX IF NOT EXISTS idx_pacientes_codigo_ibge ON pacientes(codigo_ibge);
CREATE INDEX IF NOT EXISTS idx_pacientes_cid10_codigo ON pacientes(cid10_codigo);
CREATE INDEX IF NOT EXISTS idx_medicos_codigo_ibge ON medicos(codigo_ibge);

-- Finaliza a transação, aplicando todas as alterações.
COMMIT;