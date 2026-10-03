"""
Pipeline de ETL - Vendas (Semana 10)
====================================

Extrai os CSVs brutos de "dados/origem" (clientes, produtos e vendas),
transforma e carrega no PostgreSQL (container Docker) em dois schemas:

    transformado -> as mesmas 3 tabelas da origem, limpas e tipadas
    dw           -> esquema estrela (fato_vendas + 5 dimensões)

Ao final, exporta o que foi gravado no banco para CSV:

    dados/transformado/ -> clientes.csv, produtos.csv, vendas.csv
    dados/estrela/      -> dim_*.csv e fato_vendas.csv

Pré-requisitos:
    1. PostgreSQL no ar (docker compose up -d) e ".env" configurado
    2. Dados de origem gerados: python gerar_dados_origem.py

Execução:
    python etl_vendas.py
"""
import os

from etl.config import CAMINHO_SQL, SCHEMA_DW, SCHEMA_TRANSFORMADO
from etl.conexao import obter_engine, executar_script_sql
from etl.extract import extrair_clientes, extrair_produtos, extrair_vendas
from etl.transform import (
    transformar_clientes, transformar_produtos, transformar_vendas, montar_dim_data,
)
from etl.load_transformado import carregar_transformado
from etl.load_dimensoes import (
    carregar_dim_data, carregar_dim_cliente, carregar_dim_produto,
    carregar_dim_pagamento, carregar_dim_canal,
)
from etl.load_fato_vendas import montar_fato_vendas, carregar_fato_vendas
from etl.exportar import exportar_transformado, exportar_estrela


def criar_estrutura(engine) -> None:
    executar_script_sql(engine, os.path.join(CAMINHO_SQL, "schema.sql"))


def main():
    engine = obter_engine()
    print(f"Conectando ao PostgreSQL e preparando os schemas "
          f"'{SCHEMA_TRANSFORMADO}' e '{SCHEMA_DW}'...")
    criar_estrutura(engine)

    print("\n=== 1. Extração (dados/origem) ===")
    df_clientes_bruto = extrair_clientes()
    df_produtos_bruto = extrair_produtos()
    df_vendas_bruto = extrair_vendas()
    print(f"  clientes: {len(df_clientes_bruto)} linha(s) | "
          f"produtos: {len(df_produtos_bruto)} linha(s) | "
          f"vendas: {len(df_vendas_bruto)} linha(s)")

    print("\n=== 2. Transformação ===")
    df_clientes = transformar_clientes(df_clientes_bruto)
    df_produtos = transformar_produtos(df_produtos_bruto)
    print(f"  clientes: {len(df_clientes_bruto)} linha(s) lida(s), {len(df_clientes)} válida(s).")
    print(f"  produtos: {len(df_produtos_bruto)} linha(s) lida(s), {len(df_produtos)} válida(s).")
    df_vendas = transformar_vendas(df_vendas_bruto, df_clientes, df_produtos)

    print(f"\n=== 3. Carga - schema '{SCHEMA_TRANSFORMADO}' (full load) ===")
    carregar_transformado(engine, df_clientes, df_produtos, df_vendas)
    print("  clientes, produtos e vendas recarregadas.")

    print(f"\n=== 4. Carga - schema '{SCHEMA_DW}' (esquema estrela, upsert) ===")
    carregar_dim_data(engine, montar_dim_data(df_vendas["data_venda"]))
    carregar_dim_cliente(engine, df_clientes)
    carregar_dim_produto(engine, df_produtos)
    carregar_dim_pagamento(engine, df_vendas)
    carregar_dim_canal(engine, df_vendas)
    print("  dimensões carregadas: dim_data, dim_cliente, dim_produto, dim_pagamento, dim_canal.")

    df_fato = montar_fato_vendas(engine, df_vendas)
    carregar_fato_vendas(engine, df_fato)
    print(f"  {len(df_fato)} venda(s) carregada(s) em fato_vendas.")

    print("\n=== 5. Exportação para CSV ===")
    exportar_transformado(engine)
    exportar_estrela(engine)

    print("\nETL finalizado com sucesso.")


if __name__ == "__main__":
    main()
