"""
Carga do schema "transformado": as mesmas 3 tabelas da origem (clientes,
produtos e vendas), já limpas e tipadas.

Estratégia: FULL LOAD (TRUNCATE + INSERT). Como essas tabelas são um
espelho tratado dos arquivos de origem, a cada execução elas são
esvaziadas e recarregadas por inteiro - simples e idempotente.
"""
import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from .config import SCHEMA_TRANSFORMADO


def carregar_transformado(
    engine: Engine, df_clientes: pd.DataFrame, df_produtos: pd.DataFrame, df_vendas: pd.DataFrame,
) -> None:
    """Recarrega as 3 tabelas em uma única transação: ou tudo entra, ou nada muda."""
    with engine.begin() as conn:
        # As 3 juntas no mesmo TRUNCATE por causa das chaves estrangeiras de vendas
        conn.execute(text(
            f"TRUNCATE {SCHEMA_TRANSFORMADO}.vendas, {SCHEMA_TRANSFORMADO}.clientes, "
            f"{SCHEMA_TRANSFORMADO}.produtos"
        ))
        # Ordem importa: primeiro os cadastros, depois vendas (que referencia os dois)
        for tabela, df in [("clientes", df_clientes), ("produtos", df_produtos), ("vendas", df_vendas)]:
            df.to_sql(
                tabela, con=conn, schema=SCHEMA_TRANSFORMADO, if_exists="append",
                index=False, method="multi", chunksize=1000,
            )
