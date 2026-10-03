"""
Gera o diagrama de relacionamento das tabelas (modelo entidade-
relacionamento) a partir do que existe DE FATO no PostgreSQL.

As tabelas, colunas, chaves primárias (PK) e chaves estrangeiras (FK) são
lidas do catálogo do banco (information_schema) - o desenho não é feito "à
mão", então ele sempre acompanha o schema.sql. É gerado um PNG por schema:

    diagramas/relacionamento_dw.png            (esquema estrela)
    diagramas/relacionamento_transformado.png  (tabelas tratadas)

Precisa rodar depois de "etl_vendas.py" (que cria as tabelas).

Execução:
    python gerar_diagrama.py                # os dois schemas
    python gerar_diagrama.py --schema dw    # só um schema
"""
from __future__ import annotations

import argparse
import math
import os

import matplotlib
matplotlib.use("Agg")  # não depende de interface gráfica - só salva arquivo
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Rectangle
from sqlalchemy import text

from etl.config import CAMINHO_DIAGRAMAS, SCHEMA_DW, SCHEMA_TRANSFORMADO
from etl.conexao import obter_engine

TITULOS = {
    SCHEMA_DW: "Esquema estrela - schema dw",
    SCHEMA_TRANSFORMADO: "Tabelas tratadas - schema transformado",
}

# Medidas do desenho (1 unidade = 1 polegada na figura)
LARGURA_TABELA = 3.5
ALTURA_LINHA = 0.27
ALTURA_CABECALHO = 0.42
MARGEM = 0.8

COR_CENTRAL = "#1f4e79"      # tabela central (fato / vendas)
COR_DIMENSAO = "#3f7f60"     # tabelas ao redor (dimensões / cadastros)
COR_CHAVE = "#b96a2f"        # marcadores PK / FK
COR_LINHA = "#5c6670"
COR_TEXTO = "#1c2329"
COR_TEXTO_SUAVE = "#7a858f"
COR_BORDA = "#c3cad1"
COR_ZEBRA = "#f4f6f8"

TIPOS_ABREVIADOS = {
    "character varying": "varchar",
    "character": "char",
    "timestamp without time zone": "timestamp",
    "double precision": "double",
}


# ------------------------------------------------------ leitura do catálogo ---

def buscar_colunas(engine, schema: str) -> pd.DataFrame:
    sql = text("""
        SELECT table_name AS tabela, column_name AS coluna, data_type AS tipo
        FROM information_schema.columns
        WHERE table_schema = :schema
        ORDER BY table_name, ordinal_position
    """)
    return pd.read_sql(sql, con=engine, params={"schema": schema})


def buscar_chaves_primarias(engine, schema: str) -> set[tuple[str, str]]:
    sql = text("""
        SELECT kcu.table_name AS tabela, kcu.column_name AS coluna
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON kcu.constraint_name = tc.constraint_name
         AND kcu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema = :schema
    """)
    df = pd.read_sql(sql, con=engine, params={"schema": schema})
    return set(zip(df["tabela"], df["coluna"]))


def buscar_chaves_estrangeiras(engine, schema: str) -> pd.DataFrame:
    """Uma linha por relacionamento: tabela.coluna -> tabela_ref.coluna_ref."""
    sql = text("""
        SELECT kcu.table_name AS tabela, kcu.column_name AS coluna,
               ccu.table_name AS tabela_ref, ccu.column_name AS coluna_ref
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON kcu.constraint_name = tc.constraint_name
         AND kcu.table_schema = tc.table_schema
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = :schema
        ORDER BY kcu.table_name, kcu.ordinal_position
    """)
    return pd.read_sql(sql, con=engine, params={"schema": schema})


# ------------------------------------------------------------------ layout ---

def _altura_tabela(qtd_colunas: int) -> float:
    return ALTURA_CABECALHO + qtd_colunas * ALTURA_LINHA


def calcular_posicoes(colunas: pd.DataFrame, fks: pd.DataFrame) -> tuple[str, dict]:
    """Coloca no centro a tabela com mais chaves estrangeiras (a fato) e
    distribui as demais ao redor dela - o formato de "estrela"."""
    tabelas = sorted(colunas["tabela"].unique())
    qtd_fks = fks.groupby("tabela").size()
    central = max(tabelas, key=lambda t: qtd_fks.get(t, 0))
    ao_redor = [t for t in tabelas if t != central]

    alturas = colunas.groupby("tabela").size().map(_altura_tabela)
    maior_altura_ao_redor = max((alturas[t] for t in ao_redor), default=0)

    raio_x = LARGURA_TABELA * 1.75
    raio_y = (alturas[central] / 2 + maior_altura_ao_redor / 2 + 0.7) / 0.8

    posicoes = {central: (0.0, 0.0)}
    if len(ao_redor) <= 2:
        angulos = [180, 0][:len(ao_redor)]      # esquerda e direita
    else:
        passo = 360 / len(ao_redor)
        angulos = [90 - i * passo for i in range(len(ao_redor))]  # começa no topo
    for tabela, angulo in zip(ao_redor, angulos):
        rad = math.radians(angulo)
        posicoes[tabela] = (raio_x * math.cos(rad), raio_y * math.sin(rad))
    return central, posicoes


def _ponto_na_borda(centro, destino, largura: float, altura: float):
    """Ponto em que a reta centro->destino cruza a borda do retângulo da tabela."""
    dx, dy = destino[0] - centro[0], destino[1] - centro[1]
    escalas = []
    if dx:
        escalas.append((largura / 2) / abs(dx))
    if dy:
        escalas.append((altura / 2) / abs(dy))
    t = min(escalas)
    return centro[0] + dx * t, centro[1] + dy * t


# ----------------------------------------------------------------- desenho ---

def _desenhar_tabela(ax, nome: str, centro, df_colunas: pd.DataFrame, pks, colunas_fk, cor: str) -> None:
    altura = _altura_tabela(len(df_colunas))
    x0 = centro[0] - LARGURA_TABELA / 2
    y_topo = centro[1] + altura / 2

    ax.add_patch(FancyBboxPatch(
        (x0, y_topo - altura), LARGURA_TABELA, altura,
        boxstyle="round,pad=0,rounding_size=0.06",
        facecolor="white", edgecolor=COR_BORDA, linewidth=1.2, zorder=3,
    ))
    ax.add_patch(Rectangle(
        (x0, y_topo - ALTURA_CABECALHO), LARGURA_TABELA, ALTURA_CABECALHO,
        facecolor=cor, edgecolor=cor, linewidth=1.2, zorder=4,
    ))
    ax.text(centro[0], y_topo - ALTURA_CABECALHO / 2, nome, ha="center", va="center",
            color="white", fontsize=11, fontweight="bold", zorder=5)

    for i, linha in enumerate(df_colunas.itertuples()):
        y = y_topo - ALTURA_CABECALHO - (i + 0.5) * ALTURA_LINHA
        if i % 2 == 1:
            ax.add_patch(Rectangle(
                (x0 + 0.02, y - ALTURA_LINHA / 2), LARGURA_TABELA - 0.04, ALTURA_LINHA,
                facecolor=COR_ZEBRA, edgecolor="none", zorder=4,
            ))
        eh_pk = (nome, linha.coluna) in pks
        eh_fk = linha.coluna in colunas_fk
        marcador = "PK" if eh_pk else ("FK" if eh_fk else "")
        ax.text(x0 + 0.12, y, marcador, ha="left", va="center", color=COR_CHAVE,
                fontsize=7.5, fontweight="bold", zorder=5)
        ax.text(x0 + 0.48, y, linha.coluna, ha="left", va="center", color=COR_TEXTO,
                fontsize=9, fontweight="bold" if marcador else "normal", zorder=5)
        ax.text(x0 + LARGURA_TABELA - 0.12, y, TIPOS_ABREVIADOS.get(linha.tipo, linha.tipo),
                ha="right", va="center", color=COR_TEXTO_SUAVE, fontsize=7.5, zorder=5)


def _desenhar_relacionamento(ax, origem, destino, alt_origem: float, alt_destino: float, rotulo: str) -> None:
    """Linha N:1 entre a tabela que tem a FK (origem) e a tabela referenciada."""
    p_origem = _ponto_na_borda(origem, destino, LARGURA_TABELA, alt_origem)
    p_destino = _ponto_na_borda(destino, origem, LARGURA_TABELA, alt_destino)
    ax.plot([p_origem[0], p_destino[0]], [p_origem[1], p_destino[1]],
            color=COR_LINHA, linewidth=1.6, zorder=1, solid_capstyle="round")

    dx, dy = p_destino[0] - p_origem[0], p_destino[1] - p_origem[1]
    comprimento = math.hypot(dx, dy)
    ux, uy = dx / comprimento, dy / comprimento
    estilo_cardinalidade = dict(
        ha="center", va="center", fontsize=9.5, fontweight="bold", color=COR_LINHA, zorder=6,
        bbox=dict(boxstyle="circle,pad=0.22", facecolor="white", edgecolor=COR_LINHA, linewidth=1),
    )
    ax.text(p_origem[0] + ux * 0.3, p_origem[1] + uy * 0.3, "N", **estilo_cardinalidade)
    ax.text(p_destino[0] - ux * 0.3, p_destino[1] - uy * 0.3, "1", **estilo_cardinalidade)

    ax.text((p_origem[0] + p_destino[0]) / 2, (p_origem[1] + p_destino[1]) / 2, rotulo,
            ha="center", va="center", fontsize=8, color=COR_TEXTO, zorder=6,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor=COR_BORDA, linewidth=0.8))


def gerar_diagrama(engine, schema: str) -> str | None:
    colunas = buscar_colunas(engine, schema)
    if colunas.empty:
        print(f"  [pulado] schema '{schema}': nenhuma tabela encontrada - rode etl_vendas.py antes.")
        return None
    pks = buscar_chaves_primarias(engine, schema)
    fks = buscar_chaves_estrangeiras(engine, schema)

    central, posicoes = calcular_posicoes(colunas, fks)
    alturas = {t: _altura_tabela(len(df)) for t, df in colunas.groupby("tabela")}

    x_min = min(x for x, _ in posicoes.values()) - LARGURA_TABELA / 2 - MARGEM
    x_max = max(x for x, _ in posicoes.values()) + LARGURA_TABELA / 2 + MARGEM
    y_min = min(y - alturas[t] / 2 for t, (_, y) in posicoes.items()) - MARGEM - 0.4
    y_max = max(y + alturas[t] / 2 for t, (_, y) in posicoes.items()) + MARGEM + 0.5

    fig, ax = plt.subplots(figsize=(x_max - x_min, y_max - y_min))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect("equal")
    ax.axis("off")

    for fk in fks.itertuples():
        _desenhar_relacionamento(
            ax, posicoes[fk.tabela], posicoes[fk.tabela_ref],
            alturas[fk.tabela], alturas[fk.tabela_ref],
            rotulo=fk.coluna if fk.coluna == fk.coluna_ref else f"{fk.coluna} → {fk.coluna_ref}",
        )

    for tabela, df_colunas in colunas.groupby("tabela"):
        _desenhar_tabela(
            ax, tabela, posicoes[tabela], df_colunas, pks,
            colunas_fk=set(fks.loc[fks["tabela"] == tabela, "coluna"]),
            cor=COR_CENTRAL if tabela == central else COR_DIMENSAO,
        )

    ax.text((x_min + x_max) / 2, y_max - 0.45, TITULOS.get(schema, f"Schema {schema}"),
            ha="center", va="center", fontsize=16, fontweight="bold", color=COR_TEXTO)
    ax.text((x_min + x_max) / 2, y_min + 0.4,
            "PK = chave primária   |   FK = chave estrangeira   |   "
            "N — 1: várias linhas da tabela central apontam para 1 linha da tabela ao redor",
            ha="center", va="center", fontsize=9, color=COR_TEXTO_SUAVE)

    os.makedirs(CAMINHO_DIAGRAMAS, exist_ok=True)
    caminho = os.path.join(CAMINHO_DIAGRAMAS, f"relacionamento_{schema}.png")
    fig.savefig(caminho, dpi=150, facecolor="white")
    plt.close(fig)
    return caminho


def main():
    parser = argparse.ArgumentParser(description="Gera o diagrama de relacionamento das tabelas.")
    parser.add_argument("--schema", choices=[SCHEMA_DW, SCHEMA_TRANSFORMADO],
                        help="gera só o diagrama deste schema (padrão: os dois)")
    args = parser.parse_args()

    engine = obter_engine()
    print("Lendo o catálogo do PostgreSQL e desenhando os diagramas...")
    for schema in [args.schema] if args.schema else [SCHEMA_DW, SCHEMA_TRANSFORMADO]:
        caminho = gerar_diagrama(engine, schema)
        if caminho:
            print(f"  {os.path.relpath(caminho)}")


if __name__ == "__main__":
    main()
