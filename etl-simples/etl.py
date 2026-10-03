"""
ETL simples dos arquivos da pasta PBI.

Lê os CSVs brutos (vendas, consultas de nutricionista, produtos e pedidos),
aplica as mesmas limpezas e transformações feitas à mão nos passo a passos
do Power BI / Tableau / Metabase e grava os arquivos limpos em
etl/dados_limpos/, prontos para um dashboard novo.

Uso (a partir de qualquer pasta):
    py PBI/etl/etl.py
"""
from pathlib import Path

import pandas as pd

PASTA_PBI = Path(__file__).resolve().parent.parent
PASTA_SAIDA = Path(__file__).resolve().parent / "dados_limpos"

FORMATO_DATA_ORIGEM = "%d/%m/%Y"
FORMATO_HORA_SAIDA = "%H:%M:%S"
FORMATO_DATAHORA_SAIDA = "%Y-%m-%d %H:%M:%S"

NOMES_MES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
    "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

PRODUTO_NAO_CADASTRADO = "Produto não cadastrado"
NAO_INFORMADO = "Não informado"

# Cada etapa de limpeza registra aqui o que fez (vira relatorio_qualidade.csv)
relatorio = []


def registrar(tabela, etapa, linhas_afetadas):
    relatorio.append({"tabela": tabela, "etapa": etapa, "linhas_afetadas": linhas_afetadas})


# ------------------------------------------------------------- EXTRACT ---

def ler_csv(caminho: Path) -> pd.DataFrame:
    """Lê o CSV bruto com tudo como texto: a tipagem é feita no Transform."""
    return pd.read_csv(caminho, sep=";", dtype=str, encoding="utf-8-sig", keep_default_na=False)


# ------------------------------------------------------ funções de apoio ---

def limpar_texto(serie: pd.Series) -> pd.Series:
    """Remove espaços nas pontas e espaços repetidos; texto vazio vira nulo."""
    limpo = serie.str.strip().str.replace(r"\s+", " ", regex=True)
    return limpo.mask(limpo == "")


def para_numero(serie: pd.Series) -> pd.Series:
    """'3899,90' -> 3899.9 (decimal com vírgula); vazio vira nulo."""
    return pd.to_numeric(limpar_texto(serie).str.replace(",", ".", regex=False))


def para_data(serie: pd.Series) -> pd.Series:
    return pd.to_datetime(serie, format=FORMATO_DATA_ORIGEM)


def remover_duplicatas(df: pd.DataFrame, tabela: str) -> pd.DataFrame:
    antes = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    registrar(tabela, "linhas duplicadas removidas", antes - len(df))
    return df


def contar_alterados(antes: pd.Series, depois: pd.Series) -> int:
    return int((antes.fillna("") != depois.fillna("")).sum())


# ----------------------------------------------------------- TRANSFORM ---

def transformar_vendas(bruto: pd.DataFrame) -> pd.DataFrame:
    df = bruto.copy()

    # Textos: espaços, maiúsculas/minúsculas
    for coluna in ["cliente", "categoria"]:
        novo = limpar_texto(df[coluna]).str.title()
        registrar("vendas", f"{coluna}: espaços e maiúsculas padronizados", contar_alterados(df[coluna], novo))
        df[coluna] = novo
    novo_uf = limpar_texto(df["uf"]).str.upper()
    registrar("vendas", "uf: convertida para maiúsculas", contar_alterados(df["uf"], novo_uf))
    df["uf"] = novo_uf
    for coluna in ["email", "cidade", "produto"]:
        df[coluna] = limpar_texto(df[coluna])

    # Duplicatas (comparando já com o texto limpo)
    df = remover_duplicatas(df, "vendas")

    # Tipos
    df["id_venda"] = df["id_venda"].astype(int)
    df["data_venda"] = para_data(df["data_venda"])
    df["quantidade"] = df["quantidade"].astype(int)
    df["preco_unitario"] = para_numero(df["preco_unitario"])
    df["desconto_pct"] = para_numero(df["desconto_pct"])

    # Vazios
    registrar("vendas", "desconto_pct vazio preenchido com 0", int(df["desconto_pct"].isna().sum()))
    df["desconto_pct"] = df["desconto_pct"].fillna(0)

    # Primeiro nome = primeira palavra; sobrenome = última palavra
    partes_nome = df["cliente"].str.split(" ")
    df["primeiro_nome"] = partes_nome.str[0]
    df["sobrenome"] = partes_nome.str[-1]

    df["cidade_uf"] = df["cidade"] + " - " + df["uf"]

    # Valores (sem arredondar linha a linha, para o total bater com os guias)
    df["valor_bruto"] = (df["quantidade"] * df["preco_unitario"]).round(4)
    df["valor_desconto"] = (df["valor_bruto"] * df["desconto_pct"] / 100).round(4)
    df["valor_liquido"] = (df["valor_bruto"] - df["valor_desconto"]).round(4)

    df["ano"] = df["data_venda"].dt.year
    df["mes_numero"] = df["data_venda"].dt.month
    df["mes"] = df["mes_numero"].map(lambda m: NOMES_MES[m - 1])

    return df[[
        "id_venda", "data_venda", "ano", "mes_numero", "mes",
        "cliente", "primeiro_nome", "sobrenome", "email", "cidade", "uf", "cidade_uf",
        "produto", "categoria", "quantidade", "preco_unitario", "desconto_pct",
        "valor_bruto", "valor_desconto", "valor_liquido",
    ]]


def separar_horario(horario: pd.Series) -> tuple[pd.Series, pd.Series]:
    """'08:00 - 08:50', '9:00-9:50', '14h00 - 14h50' -> (início, fim) como hora."""
    padrao = limpar_texto(horario).str.replace("h", ":", regex=False)
    partes = padrao.str.split("-", n=1, expand=True)
    inicio = pd.to_datetime(partes[0].str.strip(), format="%H:%M")
    fim = pd.to_datetime(partes[1].str.strip(), format="%H:%M")
    return inicio, fim


def transformar_consultas(bruto: pd.DataFrame) -> pd.DataFrame:
    df = bruto.copy()

    for coluna in ["paciente", "tipo_consulta"]:
        novo = limpar_texto(df[coluna]).str.title()
        registrar("consultas", f"{coluna}: espaços e maiúsculas padronizados", contar_alterados(df[coluna], novo))
        df[coluna] = novo
    for coluna in ["nutricionista", "status"]:
        df[coluna] = limpar_texto(df[coluna])

    df = remover_duplicatas(df, "consultas")

    registrar("consultas", "horario no formato 'HHhMM' corrigido", int(df["horario"].str.contains("h").sum()))
    inicio, fim = separar_horario(df["horario"])

    df["id_consulta"] = df["id_consulta"].astype(int)
    df["data_consulta"] = para_data(df["data_consulta"])
    for coluna in ["peso_kg", "altura_m", "valor"]:
        df[coluna] = para_numero(df[coluna])

    # Data + hora: o Tableau não tem tipo "só hora", então exportamos os dois
    df["inicio_datahora"] = df["data_consulta"] + (inicio - inicio.dt.normalize())
    df["fim_datahora"] = df["data_consulta"] + (fim - fim.dt.normalize())
    df["horario_inicio"] = inicio.dt.strftime(FORMATO_HORA_SAIDA)
    df["horario_fim"] = fim.dt.strftime(FORMATO_HORA_SAIDA)

    df["duracao_min"] = ((fim - inicio).dt.total_seconds() // 60).astype(int)
    df["turno"] = inicio.dt.hour.map(lambda h: "Manhã" if h < 12 else "Tarde")
    df["imc"] = (df["peso_kg"] / (df["altura_m"] ** 2)).round(1)
    df["realizada"] = (df["status"] == "Realizada").astype(int)

    registrar("consultas", "consultas sem medição (Faltou/Cancelada), peso e altura ficam vazios",
              int(df["peso_kg"].isna().sum()))

    return df[[
        "id_consulta", "data_consulta", "paciente", "nutricionista", "tipo_consulta", "status",
        "realizada", "horario_inicio", "horario_fim", "inicio_datahora", "fim_datahora",
        "duracao_min", "turno", "peso_kg", "altura_m", "imc", "valor",
    ]]


def transformar_produtos_pedidos(produtos_bruto: pd.DataFrame, pedidos_bruto: pd.DataFrame):
    produtos = produtos_bruto.copy()
    for coluna in produtos.columns:
        produtos[coluna] = limpar_texto(produtos[coluna])
    produtos["preco_unitario"] = para_numero(produtos["preco_unitario"])
    produtos = remover_duplicatas(produtos, "produtos")

    pedidos = pedidos_bruto.copy()
    for coluna in pedidos.columns:
        pedidos[coluna] = limpar_texto(pedidos[coluna])
    pedidos = remover_duplicatas(pedidos, "pedidos")
    pedidos["id_pedido"] = pedidos["id_pedido"].astype(int)
    pedidos["data_pedido"] = para_data(pedidos["data_pedido"])
    pedidos["quantidade"] = pedidos["quantidade"].astype(int)

    # Integridade referencial: pedido com produto que não existe no cadastro.
    # Em vez de apagar o pedido, criamos o produto como "não cadastrado", assim
    # o relacionamento fica íntegro e o problema continua visível no dashboard.
    orfaos = sorted(set(pedidos["id_produto"]) - set(produtos["id_produto"]))
    registrar("pedidos", f"pedidos com produto inexistente ({', '.join(orfaos) or '-'})",
              int(pedidos["id_produto"].isin(orfaos).sum()))
    if orfaos:
        produtos = pd.concat([produtos, pd.DataFrame({
            "id_produto": orfaos,
            "produto": PRODUTO_NAO_CADASTRADO,
            "categoria": NAO_INFORMADO,
            "marca": NAO_INFORMADO,
            "preco_unitario": float("nan"),
        })], ignore_index=True)

    sem_venda = sorted(set(produtos["id_produto"]) - set(pedidos["id_produto"]))
    registrar("produtos", f"produtos sem nenhuma venda ({', '.join(sem_venda) or '-'})", len(sem_venda))

    # Valor do pedido já calculado: no Tableau evita a junção só para esse cálculo
    preco = pedidos["id_produto"].map(produtos.set_index("id_produto")["preco_unitario"])
    pedidos["valor_total"] = (pedidos["quantidade"] * preco).round(4)

    produtos["qtd_pedidos"] = produtos["id_produto"].map(pedidos["id_produto"].value_counts()).fillna(0).astype(int)

    return produtos, pedidos[["id_pedido", "data_pedido", "id_produto", "quantidade", "vendedor", "valor_total"]]


# ---------------------------------------------------------------- LOAD ---

def salvar(df: pd.DataFrame, nome: str):
    """CSV no padrão brasileiro (; e vírgula decimal), datas ISO e UTF-8 com BOM."""
    caminho = PASTA_SAIDA / nome
    df.to_csv(caminho, sep=";", decimal=",", index=False, encoding="utf-8-sig",
              date_format=FORMATO_DATAHORA_SAIDA)
    print(f"  {nome:<34} {len(df):>3} linhas")


def main():
    PASTA_SAIDA.mkdir(exist_ok=True)

    print("Extract...")
    vendas_bruto = ler_csv(PASTA_PBI / "vendas.csv")
    consultas_bruto = ler_csv(PASTA_PBI / "consultas_nutricionista.csv")
    produtos_bruto = ler_csv(PASTA_PBI / "Relacionamento" / "produtos.csv")
    pedidos_bruto = ler_csv(PASTA_PBI / "Relacionamento" / "pedidos.csv")

    print("Transform...")
    vendas = transformar_vendas(vendas_bruto)
    consultas = transformar_consultas(consultas_bruto)
    produtos, pedidos = transformar_produtos_pedidos(produtos_bruto, pedidos_bruto)

    # Colunas só de data saem sem a hora (00:00:00)
    vendas["data_venda"] = vendas["data_venda"].dt.date
    consultas["data_consulta"] = consultas["data_consulta"].dt.date
    pedidos["data_pedido"] = pedidos["data_pedido"].dt.date

    print("Load...")
    salvar(vendas, "vendas.csv")
    salvar(consultas, "consultas_nutricionista.csv")
    salvar(produtos, "produtos.csv")
    salvar(pedidos, "pedidos.csv")
    salvar(pd.DataFrame(relatorio), "relatorio_qualidade.csv")

    print("\nResumo:")
    print(f"  Total de vendas ........ R$ {vendas['valor_liquido'].sum():,.2f}")
    print(f"  Consultas .............. {len(consultas)} ({consultas['realizada'].sum()} realizadas)")
    print(f"  Faturamento pedidos .... R$ {pedidos['valor_total'].sum():,.2f}")
    print(f"\nArquivos em: {PASTA_SAIDA}")


if __name__ == "__main__":
    main()
