# Dashboard de Vendas - Power BI e Tableau

Passo a passo para conectar nos dados do ETL da Semana 10 e montar um
dashboard de vendas no **Power BI** e no **Tableau**.

Há dois jeitos de trazer os dados:

| Opção | O que usar | Quando escolher |
|-------|------------|-----------------|
| **A. Arquivos CSV** | pasta [`dados/estrela/`](../dados/estrela/) | Não precisa do Docker ligado. Única opção no Tableau Public |
| **B. Banco de dados** | PostgreSQL do container (schema `dw`) | Os dados vêm tipados e com os relacionamentos prontos |

Nas duas opções use o **esquema estrela** (`fato_vendas` + 5 dimensões):
o modelo já está pronto, então o trabalho é só relacionar, criar as
medidas e montar os visuais.

> **Pré-requisito**: ter rodado o ETL (ver o [README principal](../README.md#como-executar)).
> Para a opção B, o container também precisa estar no ar.

---

## Sumário

1. [O modelo de dados](#1-o-modelo-de-dados)
2. [O dashboard que vamos montar](#2-o-dashboard-que-vamos-montar)
3. [Conexão com o banco de dados](#3-conexão-com-o-banco-de-dados)
4. [Power BI](#4-power-bi)
5. [Tableau](#5-tableau)
6. [Erros comuns](#6-erros-comuns)

---

## 1. O modelo de dados

![Esquema estrela - schema dw](../diagramas/relacionamento_dw.png)

| Tabela | Tipo | Liga na fato por | Principais campos |
|--------|------|------------------|-------------------|
| `fato_vendas` | Fato (1 linha por venda) | - | `quantidade`, `valor_total`, `valor_desconto`, `custo_total`, `lucro_bruto` |
| `dim_data` | Dimensão | `sk_data` | `data`, `ano`, `mes`, `nome_mes`, `trimestre`, `ano_mes`, `nome_dia_semana` |
| `dim_cliente` | Dimensão | `sk_cliente` | `nome`, `cidade`, `estado`, `regiao`, `sexo`, `faixa_etaria` |
| `dim_produto` | Dimensão | `sk_produto` | `nome_produto`, `categoria`, `marca`, `margem_percentual` |
| `dim_pagamento` | Dimensão | `sk_pagamento` | `forma_pagamento`, `status_pagamento` |
| `dim_canal` | Dimensão | `sk_canal` | `canal_venda` |

Todos os relacionamentos são **1 (dimensão) para N (fato)**.

> **Atenção - vendas canceladas e pendentes estão na fato.** Decida se a
> receita do dashboard conta só `status_pagamento = PAGO` e deixe isso
> explícito (com um filtro ou com a medida "Receita Paga", mais abaixo).

---

## 2. O dashboard que vamos montar

O mesmo layout nas duas ferramentas:

```
┌──────────────────────────────────────────────────────────────┬──────────┐
│  [ Receita ]   [ Lucro ]   [ Margem % ]   [ Ticket médio ]   │ FILTROS  │
├──────────────────────────────────┬───────────────────────────┤          │
│  Linha: receita por mês          │  Barras: receita por      │  Ano     │
│  (ano_mes)                       │  categoria                │  Canal   │
├──────────────────────────────────┼───────────────────────────┤  Status  │
│  Mapa / barras: receita por      │  Barras: top 10 produtos  │  Região  │
│  estado                          │                           │          │
└──────────────────────────────────┴───────────────────────────┴──────────┘
```

| Bloco | Visual | Campos |
|-------|--------|--------|
| Topo | 4 cartões (KPIs) | Receita, Lucro, Margem %, Ticket médio |
| Meio | Linha | `dim_data.ano_mes` × Receita |
| Meio | Barras | `dim_produto.categoria` × Receita |
| Baixo | Mapa ou barras | `dim_cliente.estado` × Receita |
| Baixo | Barras (top 10) | `dim_produto.nome_produto` × Receita |
| Lateral | Filtros | `ano`, `canal_venda`, `status_pagamento`, `regiao` |

Os dados vão de **janeiro de 2025 a agosto de 2026**. Comparações com o
ano anterior só fazem sentido para os meses de janeiro a agosto.

---

## 3. Conexão com o banco de dados

> Só é necessária para a **opção B**. Se for usar os CSVs, pule para a
> seção do [Power BI](#4-power-bi) ou do [Tableau](#5-tableau).

### 3.1 Os dados de conexão

| Parâmetro | Valor | De onde vem |
|-----------|-------|-------------|
| Servidor | `localhost` | O container roda na sua própria máquina |
| Porta | `5434` | `PGPORT` no [`.env`](../.env.example) |
| Banco | `vendas_dw` | `PGDATABASE` no `.env` |
| Usuário / senha | `postgres` / `postgres` | `PGUSER` / `PGPASSWORD` no `.env` |
| Schemas | `dw` (estrela) e `transformado` | [`sql/schema.sql`](../sql/schema.sql) |

### 3.2 Como a porta funciona

```
   Seu Windows                              Container Docker
┌────────────────────────┐           ┌──────────────────────────────┐
│ Power BI / Tableau     │           │  semana10_postgres           │
│ Python (etl_vendas.py) │──────────►│  PostgreSQL escutando na     │
│   localhost:5434       │  5434 →   │  porta 5432 (interna)        │
└────────────────────────┘   5432    └──────────────────────────────┘
```

- Dentro do container o PostgreSQL escuta na porta **5432**.
- A linha `"${PGPORT:-5434}:5432"` do
  [`docker-compose.yml`](../docker-compose.yml) publica essa porta como
  **5434** no Windows. É por ela que todos os programas conectam.
- **Cuidado com a 5432 no Windows**: se já existir outro PostgreSQL
  instalado na máquina, conectar em `localhost:5432` cai nesse outro
  servidor, onde o banco `vendas_dw` não existe.

O `.env` tem dois grupos de variáveis que precisam apontar para o
**mesmo** lugar:

- **`PG*`**: lidas pelo Docker Compose para criar o container.
- **`DB_*`**: lidas pelo Python em [`etl/config.py`](../etl/config.py),
  que monta a URL
  `postgresql+psycopg2://postgres:postgres@localhost:5434/vendas_dw`.

### 3.3 Antes de conectar: conferir se o banco está no ar

No terminal, dentro da pasta `Semana10/`:

```bash
# 1. O container está rodando? (deve aparecer "healthy" no STATUS)
docker ps --filter name=semana10_postgres

# 2. As tabelas do esquema estrela existem? (deve listar as 6 tabelas)
docker exec -it semana10_postgres psql -U postgres -d vendas_dw -c "\dt dw.*"
```

- Container não aparece → `docker compose up -d`
- Schema `dw` vazio → `python etl_vendas.py`

---

## 4. Power BI

### 4.1 Trazer os dados

**Opção A - arquivos CSV**

1. **Obter dados → Texto/CSV** e selecione cada um dos 6 arquivos de
   `dados/estrela/`.
2. Os CSVs usam `;` como separador e vírgula decimal, que é o padrão
   que o Power BI em português lê sem ajuste.
   > Power BI em inglês: mude `CSV_SEPARADOR=,` e `CSV_DECIMAL=.` no
   > `.env` e rode de novo `gerar_dados_origem.py` e `etl_vendas.py`.
3. Clique em **Transformar dados** e confira os tipos no Power Query:
   - `data` → **Data**
   - campos de valor (`valor_total`, `lucro_bruto`...) → **Número decimal**
   - `sk_*` → **Número inteiro**
4. Remova a coluna `dt_carga` (é só auditoria do ETL). Depois clique em
   **Fechar e aplicar**.

**Opção B - banco de dados PostgreSQL**

1. **Obter dados → Banco de dados PostgreSQL**.
2. **Servidor**: `localhost:5434` (a porta vai junto, depois dos
   dois-pontos). **Banco de dados**: `vendas_dw`.
3. **Modo de conectividade de dados**: **Importar**.
   > O *DirectQuery* consulta o banco a cada clique; só vale a pena para
   > dados muito grandes ou que mudam o tempo todo.
4. Na tela de credenciais, escolha a aba **Banco de dados** (não
   "Windows") e informe `postgres` / `postgres`.
5. Se aparecer o aviso de que a conexão **não é criptografada**, aceite:
   o container local não tem SSL configurado.
6. No **Navegador**, marque as 6 tabelas `dw.*` e clique em **Carregar**.
   > Se o Power BI reclamar da falta do provedor **Npgsql**, instale-o.
   > As versões recentes do Power BI Desktop já costumam trazê-lo.

### 4.2 Relacionamentos

1. Abra a **Exibição de modelo** (ícone de tabelas na lateral esquerda).
2. Confira as 5 ligações da `fato_vendas` com as dimensões, pelo campo de
   mesmo nome (`sk_data`, `sk_cliente`, `sk_produto`, `sk_pagamento`,
   `sk_canal`).
   - Cardinalidade: **Muitos para um (\*:1)**
   - Direção do filtro cruzado: **Única**
3. Se alguma ligação não existir, arraste o `sk_*` da fato até o `sk_*`
   da dimensão.

> Pelo banco (opção B), os relacionamentos costumam vir prontos, porque
> o Power BI lê as chaves estrangeiras. Com CSV, ele tenta detectar pelo
> nome das colunas. **Confira nos dois casos.**

### 4.3 Tabela de datas e ordenação

1. Selecione a tabela `dim_data` → **Ferramentas de tabela → Marcar como
   tabela de datas** → coluna `data`.
2. Selecione a coluna `nome_mes` → **Classificar por coluna** → `mes`.
3. Selecione a coluna `nome_dia_semana` → **Classificar por coluna** →
   `dia_semana`.

> Sem os passos 2 e 3, os meses e os dias da semana aparecem em ordem
> alfabética (Abril, Agosto, Dezembro...).

### 4.4 Medidas (DAX)

Crie uma tabela vazia para guardar as medidas (**Página Inicial → Inserir
dados** → nome `_Medidas`) e crie uma **Nova medida** para cada linha:

```dax
Receita = SUM(fato_vendas[valor_total])

Receita Paga = CALCULATE([Receita], dim_pagamento[status_pagamento] = "PAGO")

Lucro = SUM(fato_vendas[lucro_bruto])

Margem % = DIVIDE([Lucro], [Receita])

Qtd Vendas = COUNTROWS(fato_vendas)

Ticket Médio = DIVIDE([Receita], [Qtd Vendas])

Receita Ano Anterior = CALCULATE([Receita], SAMEPERIODLASTYEAR(dim_data[data]))
```

Formate `Margem %` como **Porcentagem** e as medidas de valor como
**Moeda (R$)**.

### 4.5 Montar os visuais

| Visual | Configuração |
|--------|--------------|
| 4 × **Cartão** | Receita · Lucro · Margem % · Ticket Médio |
| **Gráfico de linhas** | Eixo X: `dim_data[ano_mes]` · Eixo Y: Receita (opcional: Receita Ano Anterior) |
| **Gráfico de barras clusterizado** | Eixo Y: `dim_produto[categoria]` · Eixo X: Receita |
| **Mapa preenchido** | Local: `dim_cliente[estado]` · Saturação de cor: Receita |
| **Gráfico de barras** (top 10) | Eixo Y: `dim_produto[nome_produto]` · Eixo X: Receita · no painel **Filtros**: tipo **N superior**, 10, por Receita |
| 4 × **Segmentação de dados** | `dim_data[ano]` · `dim_canal[canal_venda]` · `dim_pagamento[status_pagamento]` · `dim_cliente[regiao]` |

> **Mapa**: selecione a coluna `estado` e, em **Ferramentas de coluna →
> Categoria de dados**, escolha **Estado ou Província**. Assim o Power BI
> não confunde a sigla (ex.: `PA`, `MA`) com outro lugar do mundo.

Por padrão, clicar em um visual filtra os outros (interação cruzada).
Ajuste em **Formatar → Editar interações** se quiser mudar.

---

## 5. Tableau

### 5.1 Trazer os dados

**Opção A - arquivos CSV** (funciona no Tableau Public e no Desktop)

1. **Conectar → Para um arquivo → Arquivo de texto** → selecione
   `dados/estrela/fato_vendas.csv`. Os outros arquivos da pasta aparecem
   na lateral esquerda.
2. **Vírgula decimal**: se os valores vierem como texto ou errados (ex.:
   `1299` em vez de `12,99`), clique na seta da fonte de dados →
   **Propriedades do arquivo de texto** → **Localidade: Português
   (Brasil)**.

**Opção B - banco de dados PostgreSQL** (somente Tableau Desktop)

1. **Conectar → Para um servidor → PostgreSQL**.
2. Preencha:
   - **Servidor**: `localhost`
   - **Porta**: `5434`
   - **Banco de dados**: `vendas_dw`
   - **Autenticação**: Nome de usuário e senha → `postgres` / `postgres`
   - **Exigir SSL**: desmarcado
3. Se pedir driver, baixe o **driver PostgreSQL** na página de drivers do
   Tableau (tableau.com/support/drivers) e reinicie o programa.
4. Em **Esquema**, escolha `dw`.

> O **Tableau Public** não conecta em PostgreSQL. Nele, use os CSVs.

### 5.2 Relacionamentos

1. Arraste `fato_vendas` para a área de modelo.
2. Arraste cada dimensão (`dim_data`, `dim_cliente`, `dim_produto`,
   `dim_pagamento`, `dim_canal`) para perto da fato. O Tableau cria um
   **relacionamento** (a linha curva, o "noodle").
3. Clique em cada relacionamento e confira se liga o `sk_*` da fato ao
   `sk_*` da dimensão.

> Use **relacionamentos** (a tela inicial do modelo), e não **joins**
> (dar dois cliques na tabela). O relacionamento respeita o grão de
> cada tabela e não duplica valores.

### 5.3 Ajustar os campos

Na aba da planilha, no painel **Dados**:

1. `sk_*` e `id_venda_origem`: clique com o botão direito → **Converter
   em dimensão**. Por serem números, o Tableau os trata como medida e
   tentaria somá-los.
2. `data` (de `dim_data`): confirme o tipo **Data**.
3. `estado` (de `dim_cliente`): botão direito → **Função geográfica →
   Estado/Província**.
4. `nome_mes`: botão direito → **Padrão → Classificar** → por campo
   `mes`, ascendente.

### 5.4 Campos calculados

Botão direito no painel Dados → **Criar campo calculado**:

```
Margem %        SUM([lucro_bruto]) / SUM([valor_total])

Ticket Médio    SUM([valor_total]) / COUNTD([id_venda_origem])

Receita Paga    SUM(IF [status_pagamento] = "PAGO" THEN [valor_total] END)
```

Formate `Margem %` como **Porcentagem** e os valores como **Moeda
(personalizado) R$**.

### 5.5 Planilhas (uma por visual)

| Planilha | Colunas | Linhas | Marcas |
|----------|---------|--------|--------|
| **KPIs** | - | - | Texto: `SUM(valor_total)`, `SUM(lucro_bruto)`, `Margem %`, `Ticket Médio` |
| **Receita mensal** | `data` (Mês contínuo) | `SUM(valor_total)` | Linha |
| **Por categoria** | `SUM(valor_total)` | `categoria` | Barra (classificar decrescente) |
| **Por estado** | (gerado) Longitude | (gerado) Latitude | Mapa: arraste `estado` para Detalhe e `SUM(valor_total)` para Cor |
| **Top 10 produtos** | `SUM(valor_total)` | `nome_produto` | Barra · filtro em `nome_produto` → **Superior → Por campo → 10** por Soma de `valor_total` |

### 5.6 Montar o painel

1. **Novo painel** (ícone na barra inferior) → tamanho **Automático** ou
   **1366 × 768**.
2. Arraste as planilhas para o painel, seguindo o layout da
   [seção 2](#2-o-dashboard-que-vamos-montar).
3. **Filtros**: em uma planilha, clique com o botão direito em `ano`,
   `canal_venda`, `status_pagamento` e `regiao` → **Mostrar filtro**.
   Em cada filtro → **Aplicar às planilhas → Todas que usam esta fonte
   de dados**.
4. **Interação**: selecione a planilha "Por categoria" no painel e clique
   no ícone de funil (**Usar como filtro**). Clicar em uma categoria
   filtra o resto do painel.

---

## 6. Erros comuns

| Sintoma | Causa provável | Solução |
|---------|----------------|---------|
| *Connection refused* / não conecta | Container parado ou porta errada | `docker compose up -d` e confira a porta **5434** |
| *database "vendas_dw" does not exist* | Conectou na **5432** (outro PostgreSQL da máquina) | Use a porta **5434** |
| *password authentication failed* | Usuário/senha diferentes do `.env` | Use os valores de `PGUSER` / `PGPASSWORD` |
| Schema `dw` vazio ou inexistente | ETL ainda não foi executado | `python etl_vendas.py` |
| Valores 100× maiores (`1299` em vez de `12,99`) | Localidade diferente da do CSV | Ajuste a localidade (Tableau) ou o `CSV_DECIMAL` no `.env` (Power BI) |
| Meses em ordem alfabética | Coluna de ordenação não configurada | Classifique `nome_mes` por `mes` |
| Valores somados errados / duplicados | Join em vez de relacionamento, ou `sk_*` tratado como medida | Use relacionamentos e converta `sk_*` em dimensão |

> **Mudou a senha no `.env` depois de o container já existir?** Ela não
> vale: o PostgreSQL só lê essas variáveis na primeira inicialização do
> volume. Para aplicar, recrie o container com `docker compose down -v`
> e `docker compose up -d` (**apaga os dados**) e rode o ETL de novo.

> **Conectar de outra máquina da rede**: use o IP do computador que roda
> o Docker no lugar de `localhost` e libere a porta **5434** no firewall
> do Windows.
