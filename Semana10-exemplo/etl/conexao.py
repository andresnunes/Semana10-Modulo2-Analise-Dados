"""
Camada de conexão com o PostgreSQL (SQLAlchemy).
"""
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .config import CONFIG_BANCO


def obter_engine() -> Engine:
    """Cria a engine de conexão com o PostgreSQL a partir do .env."""
    return create_engine(CONFIG_BANCO.url_sqlalchemy, future=True)


def executar_script_sql(engine: Engine, caminho_arquivo: str) -> None:
    """Executa um arquivo .sql (DDL) inteiro no banco."""
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        sql = f.read()
    with engine.begin() as conn:
        conn.execute(text(sql))
