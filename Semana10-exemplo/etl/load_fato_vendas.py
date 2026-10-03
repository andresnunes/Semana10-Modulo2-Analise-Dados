"""
Carga da tabela fato fato_vendas (schema "dw").

Duas etapas:
1. Resolver as chaves: trocar as chaves naturais da origem (id_cliente,
   id_produto, forma/status de pagamento, canal) pelas chaves substitutas
   (surrogate keys) das dimensões.
2. Carregar em modo UPSERT por id_venda_origem, para que o pipeline seja
   idempotente (pode ser reexecutado sem duplicar vendas).
"""
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from .config import SCHEMA_DW
from .load_dimensoes import (
    buscar_chaves_canal, buscar_chaves_cliente, buscar_chaves_pagamento,
    buscar_chaves_produto,
)

COLUNAS_FATO = [
    "id_venda", "sk_data", "sk_cliente", "sk_produto", "sk_pagamento", "sk_canal",
    "quantidade", "valor_unitario", "valor_bruto", "valor_desconto", "valor_total",
    "custo_total", "lucro_bruto",
]


def montar_fato_vendas(engine: Engine, df_vendas: pd.DataFrame) -> pd.DataFrame:
    """Substitui as chaves naturais pelas surrogate keys e calcula custo e lucro."""
    df = (
        df_vendas
        .merge(buscar_chaves_cliente(engine), on="id_cliente", how="left")
        .merge(buscar_chaves_produto(engine), on="id_produto", how="left")
        .merge(buscar_chaves_pagamento(engine), on=["forma_pagamento", "status_pagamento"], how="left")
        .merge(buscar_chaves_canal(engine), on="canal_venda", how="left")
    )
    df["sk_data"] = df["data_venda"].dt.strftime("%Y%m%d").astype(int)

    colunas_chave = ["sk_cliente", "sk_produto", "sk_pagamento", "sk_canal"]
    faltantes = df[df[colunas_chave].isna().any(axis=1)]
    if not faltantes.empty:
        print(f"  Aviso: {len(faltantes)} venda(s) descartada(s) por chave de "
              f"dimensão não encontrada.")
        df = df.drop(index=faltantes.index)

    df[colunas_chave] = df[colunas_chave].astype(int)
    df["custo_total"] = (df["quantidade"] * df["preco_custo"].astype(float)).round(2)
    df["lucro_bruto"] = (df["valor_total"] - df["custo_total"]).round(2)
    return df[COLUNAS_FATO]


def carregar_fato_vendas(engine: Engine, df: pd.DataFrame) -> None:
    sql = text(f"""
        INSERT INTO {SCHEMA_DW}.fato_vendas
            (id_venda_origem, sk_data, sk_cliente, sk_produto, sk_pagamento,
             sk_canal, quantidade, valor_unitario, valor_bruto, valor_desconto,
             valor_total, custo_total, lucro_bruto)
        VALUES
            (:id_venda, :sk_data, :sk_cliente, :sk_produto, :sk_pagamento,
             :sk_canal, :quantidade, :valor_unitario, :valor_bruto, :valor_desconto,
             :valor_total, :custo_total, :lucro_bruto)
        ON CONFLICT (id_venda_origem) DO UPDATE SET
            sk_data = EXCLUDED.sk_data,
            sk_cliente = EXCLUDED.sk_cliente,
            sk_produto = EXCLUDED.sk_produto,
            sk_pagamento = EXCLUDED.sk_pagamento,
            sk_canal = EXCLUDED.sk_canal,
            quantidade = EXCLUDED.quantidade,
            valor_unitario = EXCLUDED.valor_unitario,
            valor_bruto = EXCLUDED.valor_bruto,
            valor_desconto = EXCLUDED.valor_desconto,
            valor_total = EXCLUDED.valor_total,
            custo_total = EXCLUDED.custo_total,
            lucro_bruto = EXCLUDED.lucro_bruto,
            dt_carga = now()
    """)
    if df.empty:
        return
    with engine.begin() as conn:
        conn.execute(sql, df.to_dict(orient="records"))
