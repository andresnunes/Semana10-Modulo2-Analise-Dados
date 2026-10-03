"""
Gera os arquivos CSV que simulam a extração do sistema de vendas (OLTP)
de uma loja de suplementos e produtos saudáveis. Esses arquivos são a
FONTE (origem) do ETL e também o conjunto "bruto" para importar direto
no Power BI:

    dados/origem/clientes.csv
    dados/origem/produtos.csv
    dados/origem/vendas.csv

Os dados saem "sujos" de propósito, como costumam vir de um sistema real:
datas em dd/mm/aaaa, vírgula decimal, texto com espaços sobrando e
maiúsculas/minúsculas misturadas, campos vazios, linhas duplicadas,
vendas com quantidade zerada e vendas de clientes que não existem no
cadastro. É esse tratamento que o ETL (etl_vendas.py) resolve.

Execute:
    python gerar_dados_origem.py
"""
import os
import random
from datetime import date, timedelta

import pandas as pd
from faker import Faker

from etl.config import CAMINHO_ORIGEM, CSV_ENCODING, CSV_SEPARADOR

random.seed(42)
fake = Faker("pt_BR")
Faker.seed(42)

QTD_CLIENTES = 200
QTD_VENDAS = 3000

# Período das vendas (fixo, para os dados saírem iguais em toda execução)
DATA_VENDA_MIN = date(2025, 1, 1)
DATA_VENDA_MAX = date(2026, 8, 31)
DATA_CADASTRO_MIN = date(2023, 1, 1)
DATA_CADASTRO_MAX = date(2024, 12, 31)

# "Sujeira" inserida nos arquivos
PCT_TEXTO_SUJO = 0.15
PCT_EMAIL_VAZIO = 0.05
QTD_CLIENTES_DUPLICADOS = 6
QTD_VENDAS_DUPLICADAS = 12
QTD_VENDAS_ORFAS = 8           # cliente que não existe no cadastro
PCT_QUANTIDADE_INVALIDA = 0.015
PCT_STATUS_VAZIO = 0.03

# (id, nome, categoria, marca, preço de custo, preço de venda)
PRODUTOS = [
    (1, "Whey Protein 900g", "Suplementos", "NutriMax", 78.00, 129.90),
    (2, "Whey Protein Isolado 900g", "Suplementos", "NutriMax", 125.00, 199.90),
    (3, "Creatina 300g", "Suplementos", "PowerLab", 45.00, 79.90),
    (4, "BCAA 120 cápsulas", "Suplementos", "PowerLab", 32.00, 59.90),
    (5, "Pré-Treino 300g", "Suplementos", "PowerLab", 55.00, 99.90),
    (6, "Barra de Proteína", "Suplementos", "NutriMax", 3.20, 6.50),
    (7, "Glutamina 300g", "Suplementos", "PowerLab", 38.00, 69.90),
    (8, "Colágeno Hidrolisado 250g", "Suplementos", "VitaBem", 29.00, 54.90),
    (9, "Vitamina D 60 cápsulas", "Vitaminas", "VitaBem", 14.00, 32.00),
    (10, "Vitamina C 1g 30 comprimidos", "Vitaminas", "VitaBem", 9.50, 24.90),
    (11, "Multivitamínico 60 cápsulas", "Vitaminas", "VitaBem", 21.00, 45.00),
    (12, "Ômega 3 120 cápsulas", "Vitaminas", "OceanVit", 18.50, 38.50),
    (13, "Magnésio Dimalato 60 cápsulas", "Vitaminas", "OceanVit", 16.00, 35.90),
    (14, "Complexo B 60 cápsulas", "Vitaminas", "", 11.00, 27.90),
    (15, "Pasta de Amendoim 1kg", "Alimentos Saudáveis", "Grão Bom", 17.00, 34.90),
    (16, "Granola Sem Açúcar 500g", "Alimentos Saudáveis", "Grão Bom", 9.00, 19.90),
    (17, "Aveia em Flocos 500g", "Alimentos Saudáveis", "Grão Bom", 4.50, 9.90),
    (18, "Chia 200g", "Alimentos Saudáveis", "", 6.00, 14.90),
    (19, "Mix de Castanhas 200g", "Alimentos Saudáveis", "Grão Bom", 13.00, 27.90),
    (20, "Óleo de Coco 200ml", "Alimentos Saudáveis", "VitaBem", 10.50, 22.90),
    (21, "Isotônico 500ml", "Bebidas", "HidraFit", 2.80, 6.90),
    (22, "Bebida Proteica 250ml", "Bebidas", "NutriMax", 5.50, 11.90),
    (23, "Chá Verde 20 sachês", "Bebidas", "", 5.00, 12.90),
    (24, "Água de Coco 1L", "Bebidas", "HidraFit", 6.20, 13.90),
    (25, "Coqueteleira 600ml", "Acessórios", "PowerLab", 8.00, 24.90),
    (26, "Garrafa Térmica 1L", "Acessórios", "HidraFit", 32.00, 79.90),
    (27, "Balança Digital de Cozinha", "Acessórios", "CasaFit", 28.00, 64.90),
    (28, "Marmita Térmica", "Acessórios", "CasaFit", 35.00, 89.90),
    (29, "Porta Cápsulas", "Acessórios", "CasaFit", 4.00, 14.90),
    (30, "Squeeze 750ml", "Acessórios", "HidraFit", 9.00, 29.90),
]
PRODUTOS_INATIVOS = {23, 29}

# Cidades reais com a UF correta (algumas repetidas = mais clientes nelas)
CIDADES = [
    ("São Paulo", "SP"), ("São Paulo", "SP"), ("São Paulo", "SP"), ("Campinas", "SP"),
    ("Santos", "SP"), ("Ribeirão Preto", "SP"), ("Rio de Janeiro", "RJ"),
    ("Rio de Janeiro", "RJ"), ("Niterói", "RJ"), ("Belo Horizonte", "MG"),
    ("Belo Horizonte", "MG"), ("Uberlândia", "MG"), ("Vitória", "ES"),
    ("Curitiba", "PR"), ("Londrina", "PR"), ("Florianópolis", "SC"),
    ("Florianópolis", "SC"), ("Joinville", "SC"), ("Porto Alegre", "RS"),
    ("Caxias do Sul", "RS"), ("Salvador", "BA"), ("Recife", "PE"),
    ("Fortaleza", "CE"), ("Natal", "RN"), ("São Luís", "MA"), ("Brasília", "DF"),
    ("Goiânia", "GO"), ("Cuiabá", "MT"), ("Campo Grande", "MS"), ("Manaus", "AM"),
    ("Belém", "PA"),
]

FORMAS_PAGAMENTO = ["Pix", "Cartão de Crédito", "Cartão de Débito", "Boleto"]
PESOS_FORMA_PAGAMENTO = [40, 35, 15, 10]
STATUS_PAGAMENTO = ["Pago", "Pendente", "Cancelado"]
PESOS_STATUS_PAGAMENTO = [85, 8, 7]
CANAIS_VENDA = ["Loja Física", "Site", "Aplicativo", "Marketplace"]
PESOS_CANAL_VENDA = [35, 30, 20, 15]
DESCONTOS = ["", "", "", "", "5", "10", "15"]  # vazio = sem desconto


def _data_aleatoria(inicio: date, fim: date) -> date:
    return inicio + timedelta(days=random.randint(0, (fim - inicio).days))


def _data_br(data: date) -> str:
    return data.strftime("%d/%m/%Y")


def _decimal_br(valor: float) -> str:
    return f"{valor:.2f}".replace(".", ",")


def _sujar_texto(texto: str) -> str:
    """Em parte das linhas, bagunça maiúsculas/minúsculas e espaços."""
    if random.random() >= PCT_TEXTO_SUJO:
        return texto
    return random.choice([
        texto.upper(),
        texto.lower(),
        f"  {texto}",
        f"{texto}  ",
        f" {texto.upper()} ",
    ])


def _salvar(df: pd.DataFrame, nome_arquivo: str) -> None:
    df.to_csv(
        os.path.join(CAMINHO_ORIGEM, nome_arquivo),
        sep=CSV_SEPARADOR, index=False, encoding=CSV_ENCODING,
    )


def gerar_clientes() -> pd.DataFrame:
    registros = []
    for i in range(1, QTD_CLIENTES + 1):
        cidade, estado = random.choice(CIDADES)
        registros.append({
            "id_cliente": i,
            "nome": _sujar_texto(fake.name()),
            "cpf": fake.cpf(),
            "email": "" if random.random() < PCT_EMAIL_VAZIO else _sujar_texto(fake.email()),
            "telefone": fake.phone_number(),
            "cidade": _sujar_texto(cidade),
            "estado": _sujar_texto(estado),
            "data_nascimento": _data_br(_data_aleatoria(date(1950, 1, 1), date(2007, 12, 31))),
            "sexo": _sujar_texto(random.choice(["F", "M"])),
            "data_cadastro": _data_br(_data_aleatoria(DATA_CADASTRO_MIN, DATA_CADASTRO_MAX)),
        })
    df = pd.DataFrame(registros)

    # Clientes cadastrados em duplicidade (mesmo id, linha repetida)
    duplicados = df.sample(QTD_CLIENTES_DUPLICADOS, random_state=42)
    df = pd.concat([df, duplicados], ignore_index=True)

    _salvar(df, "clientes.csv")
    return df


def gerar_produtos() -> pd.DataFrame:
    registros = [{
        "id_produto": id_produto,
        "nome_produto": _sujar_texto(nome),
        "categoria": _sujar_texto(categoria),
        "marca": marca,
        "preco_custo": _decimal_br(custo),
        "preco_venda": _decimal_br(venda),
        "ativo": "N" if id_produto in PRODUTOS_INATIVOS else "S",
    } for id_produto, nome, categoria, marca, custo, venda in PRODUTOS]
    df = pd.DataFrame(registros)
    _salvar(df, "produtos.csv")
    return df


def gerar_vendas() -> pd.DataFrame:
    preco_por_produto = {p[0]: p[5] for p in PRODUTOS}
    ids_produto = list(preco_por_produto)

    registros = []
    for i in range(1, QTD_VENDAS + 1):
        id_produto = random.choice(ids_produto)

        quantidade = str(random.randint(1, 6))
        if random.random() < PCT_QUANTIDADE_INVALIDA:
            quantidade = random.choice(["0", ""])

        status = random.choices(STATUS_PAGAMENTO, weights=PESOS_STATUS_PAGAMENTO)[0]
        if random.random() < PCT_STATUS_VAZIO:
            status = ""

        registros.append({
            "id_venda": i,
            "data_venda": _data_br(_data_aleatoria(DATA_VENDA_MIN, DATA_VENDA_MAX)),
            "id_cliente": random.randint(1, QTD_CLIENTES),
            "id_produto": id_produto,
            "quantidade": quantidade,
            "valor_unitario": _decimal_br(preco_por_produto[id_produto]),
            "percentual_desconto": random.choice(DESCONTOS),
            "forma_pagamento": _sujar_texto(
                random.choices(FORMAS_PAGAMENTO, weights=PESOS_FORMA_PAGAMENTO)[0]
            ),
            "status_pagamento": _sujar_texto(status) if status else "",
            "canal_venda": _sujar_texto(random.choices(CANAIS_VENDA, weights=PESOS_CANAL_VENDA)[0]),
        })
    df = pd.DataFrame(registros)

    # Vendas "órfãs": apontam para um cliente que não existe no cadastro
    indices_orfas = random.sample(list(df.index), QTD_VENDAS_ORFAS)
    df.loc[indices_orfas, "id_cliente"] = [QTD_CLIENTES + 900 + n for n in range(QTD_VENDAS_ORFAS)]

    # Vendas exportadas em duplicidade (mesmo id_venda, linha repetida)
    duplicadas = df.sample(QTD_VENDAS_DUPLICADAS, random_state=42)
    df = pd.concat([df, duplicadas], ignore_index=True)

    _salvar(df, "vendas.csv")
    return df


def main():
    print("Gerando dados de origem (simulação do sistema de vendas)...")
    os.makedirs(CAMINHO_ORIGEM, exist_ok=True)

    df_clientes = gerar_clientes()
    df_produtos = gerar_produtos()
    df_vendas = gerar_vendas()

    print(f"Arquivos CSV gerados em: {CAMINHO_ORIGEM}")
    print(f" - clientes.csv ({len(df_clientes)} linhas)")
    print(f" - produtos.csv ({len(df_produtos)} linhas)")
    print(f" - vendas.csv   ({len(df_vendas)} linhas)")


if __name__ == "__main__":
    main()
