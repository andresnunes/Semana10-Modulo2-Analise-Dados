"""
Configurações do projeto: conexão com o PostgreSQL, pastas de dados e
formato dos arquivos CSV.

As credenciais são lidas de variáveis de ambiente (arquivo ".env" na raiz
do projeto). Veja ".env.example" para o modelo.
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(RAIZ_PROJETO, ".env"))


@dataclass(frozen=True)
class ConfiguracaoBanco:
    host: str = os.getenv("DB_HOST", "localhost")
    porta: str = os.getenv("DB_PORT", "5434")
    nome_banco: str = os.getenv("DB_NAME", "vendas_dw")
    usuario: str = os.getenv("DB_USER", "postgres")
    senha: str = os.getenv("DB_PASSWORD", "postgres")

    @property
    def url_sqlalchemy(self) -> str:
        return (
            f"postgresql+psycopg2://{self.usuario}:{self.senha}"
            f"@{self.host}:{self.porta}/{self.nome_banco}"
        )


CONFIG_BANCO = ConfiguracaoBanco()

SCHEMA_TRANSFORMADO = "transformado"
SCHEMA_DW = "dw"

CAMINHO_SQL = os.path.join(RAIZ_PROJETO, "sql")
CAMINHO_DIAGRAMAS = os.path.join(RAIZ_PROJETO, "diagramas")

# Os 3 conjuntos de CSV do projeto
CAMINHO_DADOS = os.path.join(RAIZ_PROJETO, "dados")
CAMINHO_ORIGEM = os.path.join(CAMINHO_DADOS, "origem")              # dados brutos
CAMINHO_TRANSFORMADO = os.path.join(CAMINHO_DADOS, "transformado")  # mesmos arquivos, tratados
CAMINHO_ESTRELA = os.path.join(CAMINHO_DADOS, "estrela")            # dimensões e fato

# Formato dos CSVs: padrão brasileiro (";" e vírgula decimal), que é o que
# o Power BI/Excel em pt-BR leem sem ajuste de localidade.
CSV_SEPARADOR = os.getenv("CSV_SEPARADOR", ";")
CSV_DECIMAL = os.getenv("CSV_DECIMAL", ",")
CSV_ENCODING = "utf-8-sig"  # UTF-8 com BOM: acentos corretos também no Excel
