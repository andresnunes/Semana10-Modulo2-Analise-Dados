"""
Camada de TRANSFORMAÇÃO (Transform).

Limpeza, padronização, tipagem e cálculo de métricas derivadas dos 3
arquivos de origem (clientes, produtos e vendas), além da montagem da
dimensão data. Recebe os DataFrames brutos (tudo texto) e devolve
DataFrames tipados, prontos para a carga.
"""
from datetime import date

import pandas as pd

FORMATO_DATA_ORIGEM = "%d/%m/%Y"

NOMES_MES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
    "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]
NOMES_DIA_SEMANA = [
    "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
    "Sexta-feira", "Sábado", "Domingo",
]

# Palavras que ficam em minúsculo ao padronizar nomes ("Maria da Silva")
PREPOSICOES = {"da", "de", "do", "das", "dos", "e"}

REGIAO_POR_UF = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte", "RO": "Norte",
    "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste",
    "PB": "Nordeste", "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste",
    "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste",
    "MS": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}

FORMAS_PAGAMENTO = {
    "PIX": "Pix",
    "CARTÃO DE CRÉDITO": "Cartão de Crédito",
    "CARTÃO DE DÉBITO": "Cartão de Débito",
    "BOLETO": "Boleto",
}

NAO_INFORMADO = "Não informado"


# ------------------------------------------------------- funções de apoio ---

def _limpar_texto(serie: pd.Series) -> pd.Series:
    """Remove espaços nas pontas e espaços duplicados; texto vazio vira nulo."""
    limpo = serie.str.strip().str.replace(r"\s+", " ", regex=True)
    return limpo.mask(limpo == "")


def _capitalizar_nome(texto):
    """'MARIA DA SILVA' -> 'Maria da Silva' (preposições em minúsculo)."""
    if pd.isna(texto):
        return texto
    palavras = texto.lower().split(" ")
    return " ".join(
        p if p in PREPOSICOES and i > 0 else p.capitalize()
        for i, p in enumerate(palavras)
    )


def _para_decimal(serie: pd.Series) -> pd.Series:
    """Converte número no padrão brasileiro ('1.299,90') em float (1299.90)."""
    texto = serie.str.strip().str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(texto, errors="coerce")


def _para_data(serie: pd.Series) -> pd.Series:
    """Converte 'dd/mm/aaaa' em data; valor inválido vira nulo (NaT)."""
    return pd.to_datetime(serie.str.strip(), format=FORMATO_DATA_ORIGEM, errors="coerce")


def _calcular_idade(data_nascimento: pd.Series, data_referencia: date) -> pd.Series:
    ref = pd.Timestamp(data_referencia)
    ainda_nao_fez_aniversario = (
        (data_nascimento.dt.month > ref.month)
        | ((data_nascimento.dt.month == ref.month) & (data_nascimento.dt.day > ref.day))
    )
    idade = ref.year - data_nascimento.dt.year - ainda_nao_fez_aniversario.astype(int)
    return idade.astype("Int64")


def _classificar_faixa_etaria(idade: pd.Series) -> pd.Series:
    faixas = pd.cut(
        idade.astype("Float64"),
        bins=[-1, 17, 24, 34, 44, 59, 200],
        labels=["Até 17", "18 a 24", "25 a 34", "35 a 44", "45 a 59", "60 ou mais"],
    )
    return faixas.astype("object").fillna(NAO_INFORMADO)


# ---------------------------------------------------------------- clientes ---

def transformar_clientes(df: pd.DataFrame, data_referencia: date | None = None) -> pd.DataFrame:
    """Padroniza o cadastro de clientes e remove duplicados.

    - texto: trim, nome/cidade capitalizados, e-mail em minúsculo, UF em maiúsculo
    - telefone: só dígitos
    - datas: dd/mm/aaaa -> DATE
    - colunas derivadas: regiao (a partir da UF), idade e faixa_etaria
    - duplicados por id_cliente: mantém a última ocorrência do arquivo
    """
    data_referencia = data_referencia or date.today()
    df = df.copy()

    df["id_cliente"] = pd.to_numeric(df["id_cliente"], errors="coerce")
    df = df.dropna(subset=["id_cliente"])
    df["id_cliente"] = df["id_cliente"].astype(int)
    df = df.drop_duplicates(subset="id_cliente", keep="last")

    df["nome"] = _limpar_texto(df["nome"]).map(_capitalizar_nome)
    df["cpf"] = _limpar_texto(df["cpf"])
    df["email"] = _limpar_texto(df["email"]).str.lower()
    df["telefone"] = _limpar_texto(df["telefone"].str.replace(r"\D", "", regex=True))
    df["cidade"] = _limpar_texto(df["cidade"]).map(_capitalizar_nome)
    df["estado"] = _limpar_texto(df["estado"]).str.upper()
    df["regiao"] = df["estado"].map(REGIAO_POR_UF).fillna(NAO_INFORMADO)
    df["sexo"] = _limpar_texto(df["sexo"]).str.upper()
    df["data_nascimento"] = _para_data(df["data_nascimento"])
    df["data_cadastro"] = _para_data(df["data_cadastro"])
    df["idade"] = _calcular_idade(df["data_nascimento"], data_referencia)
    df["faixa_etaria"] = _classificar_faixa_etaria(df["idade"])

    colunas = [
        "id_cliente", "nome", "cpf", "email", "telefone", "cidade", "estado",
        "regiao", "sexo", "data_nascimento", "idade", "faixa_etaria", "data_cadastro",
    ]
    return df[colunas].sort_values("id_cliente").reset_index(drop=True)


# ---------------------------------------------------------------- produtos ---

def transformar_produtos(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza o catálogo de produtos.

    - texto: trim; categoria capitalizada; marca vazia -> 'Sem marca'
    - preços: vírgula decimal -> NUMERIC
    - ativo: 'S'/'N' -> booleano
    - coluna derivada: margem_percentual = (venda - custo) / venda
    """
    df = df.copy()

    df["id_produto"] = pd.to_numeric(df["id_produto"], errors="coerce")
    df = df.dropna(subset=["id_produto"])
    df["id_produto"] = df["id_produto"].astype(int)
    df = df.drop_duplicates(subset="id_produto", keep="last")

    df["nome_produto"] = _limpar_texto(df["nome_produto"])
    df["categoria"] = _limpar_texto(df["categoria"]).map(_capitalizar_nome).fillna(NAO_INFORMADO)
    df["marca"] = _limpar_texto(df["marca"]).fillna("Sem marca")
    df["preco_custo"] = _para_decimal(df["preco_custo"]).round(2)
    df["preco_venda"] = _para_decimal(df["preco_venda"]).round(2)
    df["margem_percentual"] = (
        (df["preco_venda"] - df["preco_custo"]) / df["preco_venda"] * 100
    ).round(2)
    df["ativo"] = df["ativo"].str.strip().str.upper().eq("S")

    colunas = [
        "id_produto", "nome_produto", "categoria", "marca", "preco_custo",
        "preco_venda", "margem_percentual", "ativo",
    ]
    return df[colunas].sort_values("id_produto").reset_index(drop=True)


# ------------------------------------------------------------------ vendas ---

def transformar_vendas(
    df: pd.DataFrame, df_clientes: pd.DataFrame, df_produtos: pd.DataFrame,
) -> pd.DataFrame:
    """Tipa, limpa e valida as vendas, e calcula os valores da venda.

    Regras de qualidade (linhas que não passam são descartadas, com aviso):
    - id_venda duplicado: mantém a primeira ocorrência
    - data_venda inválida
    - quantidade vazia ou menor/igual a zero
    - cliente ou produto que não existe no cadastro (venda "órfã")

    Colunas derivadas: valor_bruto, valor_desconto e valor_total.
    """
    df = df.copy()
    total_lido = len(df)

    df["id_venda"] = pd.to_numeric(df["id_venda"], errors="coerce")
    df["id_cliente"] = pd.to_numeric(df["id_cliente"], errors="coerce")
    df["id_produto"] = pd.to_numeric(df["id_produto"], errors="coerce")
    df["data_venda"] = _para_data(df["data_venda"])
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce")
    df["valor_unitario"] = _para_decimal(df["valor_unitario"])
    df["percentual_desconto"] = _para_decimal(df["percentual_desconto"]).fillna(0)

    df["forma_pagamento"] = (
        _limpar_texto(df["forma_pagamento"]).str.upper().map(FORMAS_PAGAMENTO).fillna(NAO_INFORMADO)
    )
    df["status_pagamento"] = _limpar_texto(df["status_pagamento"]).str.upper().fillna("NAO_INFORMADO")
    df["canal_venda"] = _limpar_texto(df["canal_venda"]).map(_capitalizar_nome).fillna(NAO_INFORMADO)

    descartes = {}

    duplicadas = df.duplicated(subset="id_venda", keep="first")
    descartes["id_venda duplicado"] = int(duplicadas.sum())
    df = df[~duplicadas]

    sem_chave_ou_data = df[["id_venda", "id_cliente", "id_produto", "data_venda", "valor_unitario"]].isna().any(axis=1)
    descartes["id, data ou valor unitário inválido"] = int(sem_chave_ou_data.sum())
    df = df[~sem_chave_ou_data]

    quantidade_invalida = df["quantidade"].isna() | (df["quantidade"] <= 0)
    descartes["quantidade vazia ou zerada"] = int(quantidade_invalida.sum())
    df = df[~quantidade_invalida]

    orfas = ~df["id_cliente"].isin(df_clientes["id_cliente"]) | ~df["id_produto"].isin(df_produtos["id_produto"])
    descartes["cliente/produto inexistente no cadastro"] = int(orfas.sum())
    df = df[~orfas]

    for coluna in ["id_venda", "id_cliente", "id_produto", "quantidade"]:
        df[coluna] = df[coluna].astype(int)

    df["valor_unitario"] = df["valor_unitario"].round(2)
    df["valor_bruto"] = (df["quantidade"] * df["valor_unitario"]).round(2)
    df["valor_desconto"] = (df["valor_bruto"] * df["percentual_desconto"] / 100).round(2)
    df["valor_total"] = (df["valor_bruto"] - df["valor_desconto"]).round(2)

    print(f"  vendas: {total_lido} linha(s) lida(s), {len(df)} válida(s).")
    for motivo, qtd in descartes.items():
        if qtd:
            print(f"    Aviso: {qtd} linha(s) descartada(s) - {motivo}.")

    colunas = [
        "id_venda", "data_venda", "id_cliente", "id_produto", "quantidade",
        "valor_unitario", "percentual_desconto", "valor_bruto", "valor_desconto",
        "valor_total", "forma_pagamento", "status_pagamento", "canal_venda",
    ]
    return df[colunas].sort_values("id_venda").reset_index(drop=True)


# ---------------------------------------------------------------- dim_data ---

def montar_dim_data(datas: pd.Series) -> pd.DataFrame:
    """Monta a dim_data como um calendário CONTÍNUO entre a menor e a maior
    data de venda (inclui os dias sem venda - é o que o Power BI espera de
    uma tabela de datas para as funções de inteligência de tempo)."""
    calendario = pd.date_range(datas.min(), datas.max(), freq="D")
    registros = []
    for data in calendario:
        registros.append({
            "sk_data": int(data.strftime("%Y%m%d")),
            "data": data.date(),
            "dia": data.day,
            "mes": data.month,
            "nome_mes": NOMES_MES[data.month - 1],
            "trimestre": (data.month - 1) // 3 + 1,
            "ano": data.year,
            "ano_mes": data.strftime("%Y-%m"),
            "dia_semana": int(data.dayofweek),
            "nome_dia_semana": NOMES_DIA_SEMANA[data.dayofweek],
            "fim_de_semana": bool(data.dayofweek >= 5),
        })
    return pd.DataFrame(registros)
