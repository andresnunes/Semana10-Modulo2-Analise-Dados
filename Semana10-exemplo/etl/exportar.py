"""
Exportação dos resultados do ETL para CSV.

Os arquivos são gerados a partir do que está GRAVADO no PostgreSQL (e não
dos DataFrames em memória), então o CSV é sempre o retrato fiel do banco:

- dados/transformado/ -> clientes.csv, produtos.csv, vendas.csv (tratados)
- dados/estrela/      -> dim_*.csv e fato_vendas.csv (esquema estrela)
"""
import os

import pandas as pd
from sqlalchemy.engine import Engine

from .config import (
    CAMINHO_ESTRELA, CAMINHO_TRANSFORMADO, CSV_DECIMAL, CSV_ENCODING,
    CSV_SEPARADOR, SCHEMA_DW, SCHEMA_TRANSFORMADO,
)

# tabela -> coluna de ordenação
TABELAS_TRANSFORMADO = {
    "clientes": "id_cliente",
    "produtos": "id_produto",
    "vendas": "id_venda",
}
TABELAS_ESTRELA = {
    "dim_data": "sk_data",
    "dim_cliente": "sk_cliente",
    "dim_produto": "sk_produto",
    "dim_pagamento": "sk_pagamento",
    "dim_canal": "sk_canal",
    "fato_vendas": "sk_venda",
}


def _exportar_schema(engine: Engine, schema: str, tabelas: dict, pasta: str) -> None:
    os.makedirs(pasta, exist_ok=True)
    for tabela, coluna_ordem in tabelas.items():
        df = pd.read_sql(f"SELECT * FROM {schema}.{tabela} ORDER BY {coluna_ordem}", con=engine)
        caminho = os.path.join(pasta, f"{tabela}.csv")
        df.to_csv(caminho, sep=CSV_SEPARADOR, decimal=CSV_DECIMAL, index=False, encoding=CSV_ENCODING)
        print(f"  {os.path.relpath(caminho)} ({len(df)} linha(s))")


def exportar_transformado(engine: Engine) -> None:
    _exportar_schema(engine, SCHEMA_TRANSFORMADO, TABELAS_TRANSFORMADO, CAMINHO_TRANSFORMADO)


def exportar_estrela(engine: Engine) -> None:
    _exportar_schema(engine, SCHEMA_DW, TABELAS_ESTRELA, CAMINHO_ESTRELA)
