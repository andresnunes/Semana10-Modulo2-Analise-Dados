"""
Camada de EXTRAÇÃO (Extract).

Lê os arquivos CSV brutos de "dados/origem" - gerados por
"gerar_dados_origem.py" - que simulam a extração do sistema de vendas.

Tudo é lido como TEXTO, de propósito: a origem vem "suja" (datas em
dd/mm/aaaa, vírgula decimal, campos vazios), então a tipagem é
responsabilidade da camada de transformação, não da extração.
"""
import os

import pandas as pd

from .config import CAMINHO_ORIGEM, CSV_ENCODING, CSV_SEPARADOR


def _ler_csv(nome_arquivo: str) -> pd.DataFrame:
    caminho = os.path.join(CAMINHO_ORIGEM, nome_arquivo)
    return pd.read_csv(caminho, sep=CSV_SEPARADOR, dtype=str, encoding=CSV_ENCODING)


def extrair_clientes() -> pd.DataFrame:
    return _ler_csv("clientes.csv")


def extrair_produtos() -> pd.DataFrame:
    return _ler_csv("produtos.csv")


def extrair_vendas() -> pd.DataFrame:
    return _ler_csv("vendas.csv")
