-- ============================================================================
-- Vendas - Semana 10
-- Dois schemas no mesmo banco:
--   transformado -> as 3 tabelas de origem (clientes, produtos, vendas) limpas
--   dw           -> modelo dimensional (esquema estrela) para análise
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS transformado;
CREATE SCHEMA IF NOT EXISTS dw;

-- ============================================================================
-- SCHEMA transformado - mesmas tabelas da origem, já tratadas
-- ============================================================================

CREATE TABLE IF NOT EXISTS transformado.clientes (
    id_cliente         INTEGER PRIMARY KEY,
    nome               VARCHAR(120) NOT NULL,
    cpf                VARCHAR(14),
    email              VARCHAR(120),
    telefone           VARCHAR(20),
    cidade             VARCHAR(80),
    estado             CHAR(2),
    regiao             VARCHAR(20),
    sexo               VARCHAR(1),
    data_nascimento    DATE,
    idade              SMALLINT,
    faixa_etaria       VARCHAR(20),
    data_cadastro      DATE
);

CREATE TABLE IF NOT EXISTS transformado.produtos (
    id_produto           INTEGER PRIMARY KEY,
    nome_produto         VARCHAR(120) NOT NULL,
    categoria            VARCHAR(60) NOT NULL,
    marca                VARCHAR(60) NOT NULL,
    preco_custo          NUMERIC(10,2) NOT NULL,
    preco_venda          NUMERIC(10,2) NOT NULL,
    margem_percentual    NUMERIC(6,2),
    ativo                BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS transformado.vendas (
    id_venda               INTEGER PRIMARY KEY,
    data_venda             DATE NOT NULL,
    id_cliente             INTEGER NOT NULL REFERENCES transformado.clientes (id_cliente),
    id_produto             INTEGER NOT NULL REFERENCES transformado.produtos (id_produto),
    quantidade             INTEGER NOT NULL,
    valor_unitario         NUMERIC(10,2) NOT NULL,
    percentual_desconto    NUMERIC(5,2) NOT NULL,
    valor_bruto            NUMERIC(12,2) NOT NULL,
    valor_desconto         NUMERIC(12,2) NOT NULL,
    valor_total            NUMERIC(12,2) NOT NULL,
    forma_pagamento        VARCHAR(30) NOT NULL,
    status_pagamento       VARCHAR(20) NOT NULL,
    canal_venda            VARCHAR(30) NOT NULL
);

-- ============================================================================
-- SCHEMA dw - esquema estrela
-- ============================================================================

-- Dimensão Data --------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dw.dim_data (
    sk_data            INTEGER PRIMARY KEY,      -- formato AAAAMMDD
    data               DATE NOT NULL UNIQUE,
    dia                SMALLINT NOT NULL,
    mes                SMALLINT NOT NULL,
    nome_mes           VARCHAR(20) NOT NULL,
    trimestre          SMALLINT NOT NULL,
    ano                SMALLINT NOT NULL,
    ano_mes            CHAR(7) NOT NULL,         -- formato AAAA-MM
    dia_semana         SMALLINT NOT NULL,        -- 0=segunda ... 6=domingo
    nome_dia_semana    VARCHAR(15) NOT NULL,
    fim_de_semana      BOOLEAN NOT NULL
);

-- Dimensão Cliente (SCD Tipo 1 - sobrescreve, sem histórico) -------------------
CREATE TABLE IF NOT EXISTS dw.dim_cliente (
    sk_cliente           SERIAL PRIMARY KEY,
    id_cliente_origem    INTEGER NOT NULL UNIQUE,
    nome                 VARCHAR(120) NOT NULL,
    cpf                  VARCHAR(14),
    email                VARCHAR(120),
    telefone             VARCHAR(20),
    cidade               VARCHAR(80),
    estado               CHAR(2),
    regiao               VARCHAR(20),
    sexo                 VARCHAR(1),
    data_nascimento      DATE,
    faixa_etaria         VARCHAR(20),
    data_cadastro        DATE,
    dt_carga             TIMESTAMP NOT NULL DEFAULT now()
);

-- Dimensão Produto (SCD Tipo 1) ------------------------------------------------
CREATE TABLE IF NOT EXISTS dw.dim_produto (
    sk_produto           SERIAL PRIMARY KEY,
    id_produto_origem    INTEGER NOT NULL UNIQUE,
    nome_produto         VARCHAR(120) NOT NULL,
    categoria            VARCHAR(60) NOT NULL,
    marca                VARCHAR(60) NOT NULL,
    preco_custo          NUMERIC(10,2) NOT NULL,
    preco_venda          NUMERIC(10,2) NOT NULL,
    margem_percentual    NUMERIC(6,2),
    ativo                BOOLEAN NOT NULL,
    dt_carga             TIMESTAMP NOT NULL DEFAULT now()
);

-- Dimensão Pagamento (junk dimension: forma x status) --------------------------
CREATE TABLE IF NOT EXISTS dw.dim_pagamento (
    sk_pagamento        SERIAL PRIMARY KEY,
    forma_pagamento     VARCHAR(30) NOT NULL,
    status_pagamento    VARCHAR(20) NOT NULL,
    UNIQUE (forma_pagamento, status_pagamento)
);

-- Dimensão Canal de Venda --------------------------------------------------------
CREATE TABLE IF NOT EXISTS dw.dim_canal (
    sk_canal       SERIAL PRIMARY KEY,
    canal_venda    VARCHAR(30) NOT NULL UNIQUE
);

-- Fato Vendas ------------------------------------------------------------------
-- Grão: uma linha por venda (id_venda da origem = dimensão degenerada).
CREATE TABLE IF NOT EXISTS dw.fato_vendas (
    sk_venda           SERIAL PRIMARY KEY,
    id_venda_origem    INTEGER NOT NULL UNIQUE,
    sk_data            INTEGER NOT NULL REFERENCES dw.dim_data (sk_data),
    sk_cliente         INTEGER NOT NULL REFERENCES dw.dim_cliente (sk_cliente),
    sk_produto         INTEGER NOT NULL REFERENCES dw.dim_produto (sk_produto),
    sk_pagamento       INTEGER NOT NULL REFERENCES dw.dim_pagamento (sk_pagamento),
    sk_canal           INTEGER NOT NULL REFERENCES dw.dim_canal (sk_canal),
    quantidade         INTEGER NOT NULL,
    valor_unitario     NUMERIC(10,2) NOT NULL,
    valor_bruto        NUMERIC(12,2) NOT NULL,
    valor_desconto     NUMERIC(12,2) NOT NULL,
    valor_total        NUMERIC(12,2) NOT NULL,
    custo_total        NUMERIC(12,2) NOT NULL,
    lucro_bruto        NUMERIC(12,2) NOT NULL,
    dt_carga           TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_fato_vendas_data ON dw.fato_vendas (sk_data);
CREATE INDEX IF NOT EXISTS idx_fato_vendas_cliente ON dw.fato_vendas (sk_cliente);
CREATE INDEX IF NOT EXISTS idx_fato_vendas_produto ON dw.fato_vendas (sk_produto);
