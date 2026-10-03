"""
Carga das dimensões do esquema estrela (schema "dw"): data, cliente,
produto, pagamento e canal.

Todas usam UPSERT (INSERT ... ON CONFLICT) - comportamento equivalente ao
SCD Tipo 1: a dimensão sempre reflete o dado mais recente da origem, sem
manter histórico, e o pipeline pode ser reexecutado sem duplicar linhas.
"""
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from .config import SCHEMA_DW


def _registros(df: pd.DataFrame) -> list[dict]:
    """DataFrame -> lista de dicionários, trocando NaN/NaT por None (NULL)."""
    return df.astype(object).where(df.notna(), None).to_dict(orient="records")


def carregar_dim_data(engine: Engine, df: pd.DataFrame) -> None:
    sql = text(f"""
        INSERT INTO {SCHEMA_DW}.dim_data
            (sk_data, data, dia, mes, nome_mes, trimestre, ano, ano_mes,
             dia_semana, nome_dia_semana, fim_de_semana)
        VALUES
            (:sk_data, :data, :dia, :mes, :nome_mes, :trimestre, :ano, :ano_mes,
             :dia_semana, :nome_dia_semana, :fim_de_semana)
        ON CONFLICT (sk_data) DO NOTHING
    """)
    with engine.begin() as conn:
        conn.execute(sql, _registros(df))


def carregar_dim_cliente(engine: Engine, df_clientes: pd.DataFrame) -> None:
    sql = text(f"""
        INSERT INTO {SCHEMA_DW}.dim_cliente
            (id_cliente_origem, nome, cpf, email, telefone, cidade, estado,
             regiao, sexo, data_nascimento, faixa_etaria, data_cadastro)
        VALUES
            (:id_cliente, :nome, :cpf, :email, :telefone, :cidade, :estado,
             :regiao, :sexo, :data_nascimento, :faixa_etaria, :data_cadastro)
        ON CONFLICT (id_cliente_origem) DO UPDATE SET
            nome = EXCLUDED.nome,
            cpf = EXCLUDED.cpf,
            email = EXCLUDED.email,
            telefone = EXCLUDED.telefone,
            cidade = EXCLUDED.cidade,
            estado = EXCLUDED.estado,
            regiao = EXCLUDED.regiao,
            sexo = EXCLUDED.sexo,
            data_nascimento = EXCLUDED.data_nascimento,
            faixa_etaria = EXCLUDED.faixa_etaria,
            data_cadastro = EXCLUDED.data_cadastro,
            dt_carga = now()
    """)
    with engine.begin() as conn:
        conn.execute(sql, _registros(df_clientes))


def carregar_dim_produto(engine: Engine, df_produtos: pd.DataFrame) -> None:
    sql = text(f"""
        INSERT INTO {SCHEMA_DW}.dim_produto
            (id_produto_origem, nome_produto, categoria, marca, preco_custo,
             preco_venda, margem_percentual, ativo)
        VALUES
            (:id_produto, :nome_produto, :categoria, :marca, :preco_custo,
             :preco_venda, :margem_percentual, :ativo)
        ON CONFLICT (id_produto_origem) DO UPDATE SET
            nome_produto = EXCLUDED.nome_produto,
            categoria = EXCLUDED.categoria,
            marca = EXCLUDED.marca,
            preco_custo = EXCLUDED.preco_custo,
            preco_venda = EXCLUDED.preco_venda,
            margem_percentual = EXCLUDED.margem_percentual,
            ativo = EXCLUDED.ativo,
            dt_carga = now()
    """)
    with engine.begin() as conn:
        conn.execute(sql, _registros(df_produtos))


def carregar_dim_pagamento(engine: Engine, df_vendas: pd.DataFrame) -> None:
    """Junk dimension: uma linha para cada combinação forma x status que
    aparece nas vendas."""
    combinacoes = df_vendas[["forma_pagamento", "status_pagamento"]].drop_duplicates()
    sql = text(f"""
        INSERT INTO {SCHEMA_DW}.dim_pagamento (forma_pagamento, status_pagamento)
        VALUES (:forma_pagamento, :status_pagamento)
        ON CONFLICT (forma_pagamento, status_pagamento) DO NOTHING
    """)
    with engine.begin() as conn:
        conn.execute(sql, _registros(combinacoes.sort_values(["forma_pagamento", "status_pagamento"])))


def carregar_dim_canal(engine: Engine, df_vendas: pd.DataFrame) -> None:
    canais = df_vendas[["canal_venda"]].drop_duplicates().sort_values("canal_venda")
    sql = text(f"""
        INSERT INTO {SCHEMA_DW}.dim_canal (canal_venda)
        VALUES (:canal_venda)
        ON CONFLICT (canal_venda) DO NOTHING
    """)
    with engine.begin() as conn:
        conn.execute(sql, _registros(canais))


def buscar_chaves_cliente(engine: Engine) -> pd.DataFrame:
    return pd.read_sql(
        f"SELECT sk_cliente, id_cliente_origem AS id_cliente FROM {SCHEMA_DW}.dim_cliente",
        con=engine,
    )


def buscar_chaves_produto(engine: Engine) -> pd.DataFrame:
    """Traz também o preço de custo, usado para calcular o custo/lucro da venda."""
    return pd.read_sql(
        f"SELECT sk_produto, id_produto_origem AS id_produto, preco_custo FROM {SCHEMA_DW}.dim_produto",
        con=engine,
    )


def buscar_chaves_pagamento(engine: Engine) -> pd.DataFrame:
    return pd.read_sql(
        f"SELECT sk_pagamento, forma_pagamento, status_pagamento FROM {SCHEMA_DW}.dim_pagamento",
        con=engine,
    )


def buscar_chaves_canal(engine: Engine) -> pd.DataFrame:
    return pd.read_sql(f"SELECT sk_canal, canal_venda FROM {SCHEMA_DW}.dim_canal", con=engine)
