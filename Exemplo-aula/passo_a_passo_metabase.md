# Metabase: limpeza, transformação, agregação e relacionamento

São os mesmos exercícios do [passo a passo do Power BI](passo_a_passo_power_bi.md), feitos agora no **Metabase**, uma ferramenta de BI open source que roda no navegador.

| Dados | Conteúdo | Objetivo principal |
|---|---|---|
| `bruto.vendas` (de `vendas.csv`) | Vendas com dados do cliente e do produto | **Primeiro nome** e **sobrenome**, **total de vendas** |
| `bruto.consultas_nutricionista` (de `consultas_nutricionista.csv`) | Agenda de consultas de nutricionistas | **Horário de início** e **horário de fim**, **contagem de consultas** |
| `loja.produtos` (de `Relacionamento/produtos.csv`) | Cadastro de produtos (10 linhas) | Tabela **dimensão** (lado "1") |
| `loja.pedidos` (de `Relacionamento/pedidos.csv`) | Pedidos, apenas com o `id_produto` (30 linhas) | Tabela **fato** (lado "muitos") |

> 💡 **Diferença importante em relação ao Power BI e ao Tableau:** o Metabase **não lê o CSV direto** para tratar os dados. Ele se conecta a um **banco de dados**. Por isso, a pasta `Metabase/` sobe um **PostgreSQL** com os CSVs carregados **brutos**, todos como texto e com os mesmos problemas de antes. A limpeza é feita **dentro do Metabase**, de duas formas:
> - **Editor visual** (*notebook*): blocos de Filtro, Resumir, Coluna personalizada e Juntar dados, sem escrever código;
> - **SQL**, salvo como **Modelo**, para o que o editor visual não faz (converter `3899,90` em número, `dd/mm/aaaa` em data, colocar cada palavra em maiúscula).
>
> Os menus estão em português; entre parênteses aparece o nome em inglês, porque a tradução muda um pouco entre as versões.

### Fluxo geral da aula

```
 CSVs ──► PostgreSQL ──► Metabase: ──► Modelos ──────────► Perguntas ──► Painel
          (schema        Navegar      (SQL de limpeza,     (Resumir,     (filtros
           bruto/loja)   pelos dados   uma "tabela limpa") agrupar)       ligados)
                                       + Modelo de dados (relacionamento)
```

---

## Parte 0: Subir o ambiente

### 0.1 Docker

Na pasta `PBI/Metabase/`, rode no terminal:

```bash
docker compose up -d
```

- **Postgres:** porta `5435`, banco `aula_bi`, usuário e senha `postgres`. Na primeira subida, ele executa `init/01_carga.sql`, que cria os schemas `bruto` e `loja` e carrega os CSVs.
- **Metabase:** abra **http://localhost:3000**. A primeira inicialização leva de **1 a 2 minutos**.

> ⚠️ O script de carga **só roda na primeira vez**. Para recarregar do zero: `docker compose down -v` e depois `docker compose up -d`.

### 0.2 Configuração inicial do Metabase (só na primeira vez)

| # | Tela | Clique | O que acontece |
|---|---|---|---|
| 1 | Boas-vindas | **Vamos começar** (Let's get started) | |
| 2 | Idioma | **Português (Brasil)** › **Próximo** | A interface fica em português |
| 3 | Usuário | Preencha nome, e-mail e senha do administrador › **Próximo** | |
| 4 | Adicionar dados | Escolha **PostgreSQL** | Abre o formulário de conexão |
| 5 | Formulário | Nome exibido `Aula BI` · Host `postgres` · Porta `5432` · Nome do banco `aula_bi` · Usuário `postgres` · Senha `postgres` › **Conectar banco de dados** | |
| 6 | Últimas telas | **Próximo** › **Terminar** › **Leve-me ao Metabase** | Abre a página inicial |

> 💡 O Host é `postgres`, e não `localhost`, porque o Metabase está **dentro** do Docker e enxerga o banco pelo nome do serviço.

### 0.3 Mapa das telas

Nas tabelas de cliques, as letras entre colchetes indicam a área da tela.

**Página inicial**

```
+---------------------------------------------------------------------------------+
| [A] BARRA SUPERIOR:  [=] (menu)   Busca...            [+ Novo]   [engrenagem]   |
|                                                        Pergunta   Configurações |
|                                                        Consulta   de admin.     |
|                                                        SQL                      |
|                                                        Painel                   |
|                                                        Modelo                   |
+----------------------+----------------------------------------------------------+
| [B] BARRA LATERAL    | [C] CONTEÚDO                                             |
|  Início              |   Coleções, perguntas salvas, painéis...                 |
|  Coleções            |                                                          |
|   Nossa análise      |                                                          |
|  Navegar             |                                                          |
|   Modelos            |                                                          |
|   Bancos de dados    |                                                          |
+----------------------+----------------------------------------------------------+
```

**Editor visual de perguntas (notebook)**

```
+---------------------------------------------------------------------------------+
| [D] Título da pergunta                  [ícone do editor]   [Salvar]            |
+---------------------------------------------------------------------------------+
| [E] BLOCOS (de cima para baixo = ordem de execução)                             |
|   Dados ............ [ Aula BI > Bruto > Vendas ]   [Juntar dados] [Coluna pers.]|
|   Filtro ........... [ + Adicionar filtros ]                                    |
|   Resumir .......... [ Escolha uma métrica ]  por  [ Escolha uma coluna ]       |
|   [Ordenar] [Limite]                                                            |
|                                                                                 |
|                      [ Visualizar ]  <- executa e mostra o resultado             |
+---------------------------------------------------------------------------------+
```

**Resultado de uma pergunta**

```
+---------------------------------------------------------------------------------+
| [D] Título         [Filtro] [Resumir] [ícone do editor]           [Salvar]      |
+---------------------------------------------------------------------------------+
| [F] RESULTADO (tabela ou gráfico)                                               |
|     clique num valor ou num cabeçalho = menu de ações (filtrar, agrupar...)     |
+---------------------------------------------------------------------------------+
| [G] [Visualização] [engrenagem]   "Mostrando 305 linhas"  [tabela <-> gráfico]  |
|     (tipo de gráfico) (config.)                                                 |
+---------------------------------------------------------------------------------+
```

**Editor SQL**: [A] **+ Novo** › **Consulta SQL** (SQL query). Escolha o banco `Aula BI`, digite o SQL e execute com o botão **▶** ou com **Ctrl + Enter**.

---

## Parte 1: Conhecer os dados brutos

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [B] | **Navegar** › **Bancos de dados** › **Aula BI** | Mostra os schemas **Bruto** e **Loja** |
| 2 | Schema Bruto | Clique em **Vendas** | Abre a tabela: "Mostrando 305 linhas" em [G] |
| 3 | [F] | Clique no cabeçalho **Categoria** › **Distribuição** | Gráfico com **9 valores**, com grafias diferentes da mesma categoria |
| 4 | [F] | Observe `Preco Unitario` (`3899,90`) e `Data Venda` (`05/01/2026`) | Estão como **texto**, alinhados à esquerda |

> 💡 O Metabase também **renomeia as colunas** para exibição: `id_venda` vira **Id Venda**. No SQL, porém, os nomes continuam os originais (`id_venda`).

---

## Parte 2: Vendas

### 2.1 Limpeza no editor visual (sem código)

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **+ Novo** › **Pergunta** (Question) › **Bancos de dados brutos** › **Aula BI** › **Bruto** › **Vendas** | Abre o editor [E] |
| 2 | [E] bloco Dados | Ícone **Coluna personalizada** (Custom column) | Abre o editor de expressão |
| 3 | Editor | Expressão `upper(trim([Uf]))` · Nome `UF Limpa` › **Concluído** | Ao digitar `[`, o Metabase lista as colunas |
| 4 | [E] | Repita o passo 2 para as colunas abaixo | |
| 5 | [E] | **Visualizar** | As colunas novas ficam no fim da tabela |

| Nome | Expressão |
|---|---|
| `UF Limpa` | `upper(trim([Uf]))` |
| `Cliente Limpo` | `trim([Cliente])` |
| `Categoria Limpa` | `upper(trim([Categoria]))` |
| `Primeiro Nome` | `regexExtract(trim([Cliente]), "^(\S+)")` |
| `Sobrenome` | `regexExtract(trim([Cliente]), "(\S+)$")` |
| `Cidade UF` | `concat([Cidade], " - ", upper(trim([Uf])))` |

- `regexExtract` usa uma expressão regular:
  - `^(\S+)` pega a primeira palavra (`^` = início, `\S+` = caracteres que não são espaço);
  - `(\S+)$` pega a última palavra (`$` = fim).
- Nas versões recentes, também existe o atalho **Combinar colunas** (Combine columns) no bloco Coluna personalizada, que monta o `concat` com cliques.

> ⚠️ **Limites do editor visual:**
> - não tem "Colocar cada palavra em maiúscula": `carlos eduardo lima` fica minúsculo, e por isso usamos `upper` na categoria;
> - não converte `3899,90` em número nem `05/01/2026` em data;
> - não remove linhas duplicadas.
>
> Para isso, usamos SQL (2.2).

### 2.2 ⭐ Limpeza completa em SQL, salva como Modelo

Um **Modelo** (Model) é uma "tabela limpa" virtual. As perguntas usam o modelo como se fosse uma tabela comum, e o SQL fica escondido.

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **+ Novo** › **Modelo** (Model) › **Usar uma consulta SQL nativa** (Use a native query) | Abre o editor SQL do modelo |
| 2 | Editor | Banco = **Aula BI** › cole o SQL abaixo › **▶** | 300 linhas limpas |
| 3 | Aba **Metadados** (Metadata) | Clique na coluna `valor_liquido` › Tipo de coluna = **Moeda** (Currency) | Formatação em R$ |
| 4 | Aba Metadados | Clique em `id_venda` › Tipo = **Chave de entidade** (Entity Key) | O Metabase não vai somar o ID |
| 5 | Topo | **Salvar** › Nome `Vendas (limpo)` › Coleção **Nossa análise** | O modelo aparece em [B] › Navegar › **Modelos** |

```sql
WITH limpo AS (
    SELECT DISTINCT                                              -- remove as 5 linhas duplicadas
        id_venda::int                                         AS id_venda,
        to_date(data_venda, 'DD/MM/YYYY')                     AS data_venda,
        initcap(trim(cliente))                                AS cliente,
        email,
        cidade,
        upper(trim(uf))                                       AS uf,
        produto,
        initcap(trim(categoria))                              AS categoria,
        quantidade::int                                       AS quantidade,
        replace(preco_unitario, ',', '.')::numeric            AS preco_unitario,
        coalesce(replace(desconto_pct, ',', '.')::numeric, 0) AS desconto_pct
    FROM bruto.vendas
)
SELECT
    *,
    split_part(cliente, ' ', 1)                           AS primeiro_nome,
    split_part(cliente, ' ', -1)                          AS sobrenome,
    cidade || ' - ' || uf                                 AS cidade_uf,
    quantidade * preco_unitario                           AS valor_bruto,
    quantidade * preco_unitario * (1 - desconto_pct / 100) AS valor_liquido
FROM limpo
```

| Etapa do Power Query | Equivalente no SQL |
|---|---|
| Cortar | `trim(...)` |
| Colocar Cada Palavra Em Maiúscula | `initcap(...)` |
| MAIÚSCULAS | `upper(...)` |
| Remover Duplicatas | `SELECT DISTINCT` |
| Substituir `null` por `0` | `coalesce(..., 0)` |
| Alterar tipo (decimal pt-BR) | `replace(x, ',', '.')::numeric` |
| Alterar tipo (data dd/mm/aaaa) | `to_date(x, 'DD/MM/YYYY')` |
| Texto Antes do Delimitador | `split_part(cliente, ' ', 1)` |
| Texto Após o Delimitador (do final) | `split_part(cliente, ' ', -1)` |
| Mesclar Colunas | `cidade \|\| ' - ' \|\| uf` |
| Coluna Personalizada | `quantidade * preco_unitario ...` |

| cliente | primeiro_nome | sobrenome | cidade_uf |
|---|---|---|---|
| Ana Paula Ribeiro | Ana | Ribeiro | Florianópolis - SC |
| Carlos Eduardo Lima | Carlos | Lima | São José - SC |
| João Pedro Almeida | João | Almeida | Curitiba - PR |

> 🔎 **Demonstração da duplicata:** faça uma pergunta na tabela **Bruto › Vendas** com Resumir = **Contagem de linhas** (305) e outra com **Número de valores distintos de** `Id Venda` (300).

### 2.3 ⭐ Agregação (Resumir)

No Metabase, o "Agrupar Por" é o bloco **Resumir** (Summarize): métrica **por** coluna.

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **+ Novo** › **Pergunta** › **Modelos** › **Vendas (limpo)** | |
| 2 | [E] Resumir | **Escolha uma métrica** › **Soma de ...** › `Valor Liquido` | |
| 3 | [E] Resumir | Botão **+** ao lado da métrica › **Contagem de linhas** | |
| 4 | [E] Resumir | **+** › **Soma de ...** › `Quantidade` · **+** › **Média de ...** › `Valor Liquido` | |
| 5 | [E] Resumir | **Escolha uma coluna para agrupar** › `Categoria` | |
| 6 | [E] | **Visualizar** | O Metabase já mostra um **gráfico de barras** |
| 7 | [G] | Botão **tabela** (canto direito do rodapé) | Mostra os números em tabela |
| 8 | [D] | **Salvar** › `Vendas por Categoria` | |

**Resultado esperado:**

| Categoria | Contagem | Soma de Valor Liquido |
|---|---|---|
| Eletrônicos | 88 | 166.540,71 |
| Informática | 114 | 183.316,02 |
| Móveis | 98 | 121.527,90 |

**Atalho sem abrir o editor:** no resultado do modelo [F], clique no cabeçalho `Categoria` › **Distribuição**, ou clique em `Valor Liquido` › **Soma**, e depois agrupe.

**Exercício:** agrupe por `Primeiro Nome` e `Sobrenome` (use o **+** do agrupamento). Depois clique no cabeçalho da métrica › **Ordenar decrescente**. Quem mais comprou?

### 2.4 ⭐ Total de vendas

O valor esperado é **R$ 471.384,63** (300 vendas, 602 itens).

**Forma A: pergunta com o número**

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **+ Novo** › **Pergunta** › **Modelos** › **Vendas (limpo)** | |
| 2 | [E] Resumir | **Soma de ...** › `Valor Liquido` (**sem** agrupar) › **Visualizar** | Um número grande: **R$ 471.384,63** |
| 3 | [G] | **Visualização** › **Número** (Number) | Já costuma vir assim |
| 4 | [D] | **Salvar** › `Total de Vendas` | |

**Forma B: métrica com expressão personalizada** (parecida com a medida DAX)

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [E] Resumir | **Escolha uma métrica** › **Expressão personalizada** (Custom Expression) | |
| 2 | Editor | `Sum([Quantidade] * [Preco Unitario])` · Nome `Total Bruto` › **Concluído** | R$ 498.954,80, antes do desconto |
| 3 | Editor | `Sum([Valor Bruto]) - Sum([Valor Liquido])` · Nome `Total de Descontos` | |

> 💡 Nas versões recentes existe **+ Novo › Métrica** (Metric): uma agregação salva, reutilizável em várias perguntas, como uma medida do Power BI.

**Forma C: SQL**

```sql
SELECT round(sum(valor_liquido), 2) AS total_de_vendas
FROM {{#1-vendas-limpo}}
```

> 💡 `{{#1-vendas-limpo}}` referencia o **modelo** salvo, e o número é o ID do modelo. No editor SQL, digite `{{#` e o Metabase sugere o nome. Também dá para consultar direto a tabela bruta, mas aí seria preciso repetir toda a limpeza.

**Demonstração com filtro:** no painel (Parte 4), adicione um filtro de **Categoria**. Escolha "Móveis" e o total vira **R$ 121.527,90**.

---

## Parte 3: Consultas de nutricionista

### 3.1 Horário de início e fim no editor visual

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **+ Novo** › **Pergunta** › **Aula BI** › **Bruto** › **Consultas Nutricionista** | |
| 2 | [E] | **Coluna personalizada**, com as expressões abaixo › **Visualizar** | |

| Nome | Expressão | `14h00 - 14h50` vira |
|---|---|---|
| `Horario Padrao` | `replace([Horario], "h", ":")` | `14:00 - 14:50` |
| `Inicio Texto` | `regexExtract(replace([Horario], "h", ":"), "^\s*([0-9:]+)")` | `14:00` |
| `Fim Texto` | `regexExtract(replace([Horario], "h", ":"), "([0-9:]+)\s*$")` | `14:50` |
| `Paciente Limpo` | `trim([Paciente])` | |

> ⚠️ O resultado ainda é **texto**: sem o tipo hora, não dá para calcular a duração. Isso fica para o SQL (3.2).

### 3.2 ⭐ Modelo SQL "Consultas (limpo)"

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **+ Novo** › **Modelo** › **Usar uma consulta SQL nativa** | |
| 2 | Editor | Banco **Aula BI** › cole o SQL › **▶** | **221 linhas** (saem 4 consultas duplicadas) |
| 3 | Metadados | `id_consulta` = **Chave de entidade** · `valor` = **Moeda** | |
| 4 | Topo | **Salvar** › `Consultas (limpo)` | |

```sql
WITH limpo AS (
    SELECT DISTINCT
        id_consulta::int                      AS id_consulta,
        to_date(data_consulta, 'DD/MM/YYYY')  AS data_consulta,
        initcap(trim(paciente))               AS paciente,
        nutricionista,
        replace(horario, 'h', ':')            AS horario,
        initcap(trim(tipo_consulta))          AS tipo_consulta,
        status,
        replace(peso_kg, ',', '.')::numeric   AS peso_kg,
        replace(altura_m, ',', '.')::numeric  AS altura_m,
        replace(valor, ',', '.')::numeric     AS valor
    FROM bruto.consultas_nutricionista
),
horarios AS (
    SELECT
        *,
        trim(split_part(horario, '-', 1))::time AS horario_inicio,   -- antes do "-"
        trim(split_part(horario, '-', 2))::time AS horario_fim       -- depois do "-"
    FROM limpo
)
SELECT
    id_consulta, data_consulta, paciente, nutricionista, tipo_consulta, status,
    horario_inicio,
    horario_fim,
    extract(epoch FROM horario_fim - horario_inicio)::int / 60      AS duracao_min,
    data_consulta + horario_inicio                                  AS inicio_datahora,
    CASE WHEN horario_inicio < '12:00' THEN 'Manhã' ELSE 'Tarde' END AS turno,
    peso_kg,
    altura_m,
    round(peso_kg / (altura_m * altura_m), 1)                       AS imc,
    valor
FROM horarios
```

| horario (bruto) | horario_inicio | horario_fim | duracao_min | turno |
|---|---|---|---|---|
| `08:30-09:20` | 08:30 | 09:20 | 50 | Manhã |
| `9:00-9:50` | 09:00 | 09:50 | 50 | Manhã |
| `14h00 - 14h50` | 14:00 | 14:50 | 50 | Tarde |

As consultas com status *Faltou* ou *Cancelada* ficam com peso, altura e IMC **vazios**, e isso está correto.

### 3.3 ⭐ Agregação por nutricionista

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **+ Novo** › **Pergunta** › **Modelos** › **Consultas (limpo)** | |
| 2 | [E] Filtro | **+ Adicionar filtros** › `Status` › marque **Realizada** › **Adicionar filtro** | 178 linhas |
| 3 | [E] Resumir | **Contagem de linhas** · **+** Soma de `Valor` · **+** Média de `Duracao Min` · **+** Soma de `Duracao Min` | |
| 4 | [E] Resumir | Agrupar por `Nutricionista` › **Visualizar** | 3 linhas: André **62**, Camila **58** e Luiza **58** consultas |
| 5 | [D] | **Salvar** › `Resumo por Nutricionista` | |

Duração média: Camila **36,7**, Luiza **33,4**, André **33,5** minutos.

**Exercício:** agrupe por `Nutricionista` **e** `Tipo Consulta`.

### 3.4 ⭐ Contagem de consultas

Valores esperados: **221 consultas no total**, sendo **178 Realizadas**, **31 Faltou** e **12 Cancelada**.

**Forma A: Contagem de linhas**

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **+ Novo** › **Pergunta** › **Modelos** › **Consultas (limpo)** | |
| 2 | [E] Resumir | **Contagem de linhas** › **Visualizar** | **221** |
| 3 | [D] | Botão **Filtro** › `Status` › **Realizada** | **178** |

> 💬 **Ponto para a turma:** no Power BI e no Tableau, arrastar o ID para um cartão **soma** os IDs (24.531 ou 24.894). No Metabase, uma coluna marcada como **Chave de entidade** nem aparece em "Soma de…". O tipo semântico evita o erro.

**Forma B: várias contagens numa pergunta só (expressões personalizadas)**

[E] Resumir › **Escolha uma métrica** › **Expressão personalizada**, uma por métrica:

| Nome | Expressão | Resultado |
|---|---|---|
| `Total de Consultas` | `Count()` | 221 |
| `Consultas Realizadas` | `CountIf([Status] = "Realizada")` | 178 |
| `Ausências` | `CountIf([Status] != "Realizada")` | 43 |
| `Taxa de Ausência` | `CountIf([Status] != "Realizada") / Count()` | 0,195 |
| `Pacientes Atendidos` | `DistinctIf([Paciente], [Status] = "Realizada")` | 32 |

Para ver **19,5%**: [G] **engrenagem** › clique em `Taxa de Ausência` › Estilo = **Porcentagem**.

> Se a sua versão não tiver `DistinctIf`, use um filtro `Status = Realizada` e a métrica **Número de valores distintos de** `Paciente`.

**Gráfico por status**

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | Nova pergunta em **Consultas (limpo)** | Resumir **Contagem de linhas** por `Status` › **Visualizar** | Barras: Realizada 178, Faltou 31, Cancelada 12 |
| 2 | [E] Resumir | Adicione um 2º agrupamento: `Nutricionista` › **Visualizar** | Barras por status e nutricionista |
| 3 | [G] | **engrenagem** › **Exibir** › **Empilhar** (Stack) | Barras empilhadas |
| 4 | [G] | **Visualização** › **Pizza** (Pie), só com o agrupamento por Status | Proporção de cada status |

Por tipo (realizadas): Retorno **137**, Primeira Consulta **21**, Avaliação Esportiva **20**.

**Forma C: SQL**

```sql
SELECT
    count(*)                                             AS total_de_consultas,
    count(*) FILTER (WHERE status = 'Realizada')         AS consultas_realizadas,
    count(*) FILTER (WHERE status <> 'Realizada')        AS ausencias,
    round(count(*) FILTER (WHERE status <> 'Realizada') * 100.0 / count(*), 1) AS taxa_ausencia_pct
FROM {{#2-consultas-limpo}}
```

---

## Parte 4: Painel (Dashboard)

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **+ Novo** › **Painel** (Dashboard) › Nome `Aula BI` › **Criar** | Painel vazio em modo de edição |
| 2 | Topo do painel | Ícone **+** (Adicionar uma pergunta) › escolha `Total de Vendas`, `Vendas por Categoria`, `Resumo por Nutricionista`… | Os cartões aparecem; arraste pelas bordas para redimensionar |
| 3 | Topo do painel | Ícone de **filtro** › **Texto ou categoria** › **É** | Aparece um filtro vazio |
| 4 | Cada cartão | Clique em **Selecione…** › `Categoria` | O filtro fica **ligado** às perguntas de vendas |
| 5 | Topo | **Salvar** | |
| 6 | Filtro | Escolha **Móveis** | O total vira **R$ 121.527,90** e o gráfico fica só com Móveis |

---

## Parte 5: ⭐ Relacionamento entre tabelas

```
        loja.produtos  (dimensão)                   loja.pedidos  (fato)
  +---------------------------+              +---------------------------+
  | id_produto  (PK)      [1] |------------<*| id_produto  (FK)          |
  | produto                   |   1 : muitos | id_pedido   (PK)          |
  | categoria                 |              | data_pedido               |
  | marca                     |              | quantidade                |
  | preco_unitario            |              | vendedor                  |
  +---------------------------+              +---------------------------+
```

- De propósito, o banco **não tem** a chave estrangeira. Nós vamos "ensinar" o relacionamento ao Metabase.
- Há duas "armadilhas" nos dados, colocadas de propósito:
  - o produto **P10** (Luminária) **nunca foi vendido**;
  - o pedido **14** usa o **P11**, que **não existe** no cadastro.
- Essas tabelas já estão com os tipos corretos, porque o foco aqui é o relacionamento.

### 5.1 Primeiro, SEM relacionamento (para ver o problema)

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **+ Novo** › **Pergunta** › **Aula BI** › **Loja** › **Pedidos** | |
| 2 | [E] Resumir | **Soma de ...** › `Quantidade` | |
| 3 | [E] Resumir | **Escolha uma coluna para agrupar** › procure `Categoria` | ❌ **Não existe**: só aparecem colunas de Pedidos |

> 💬 A tabela `pedidos` só tem o código do produto. Sem relacionamento, o Metabase não sabe onde buscar a categoria.

### 5.2 Criar o relacionamento (Modelo de dados)

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **engrenagem** › **Configurações de administrador** (Admin settings) | |
| 2 | Menu superior do admin | **Modelo de dados** / **Metadados da tabela** (Table Metadata) | |
| 3 | Lista à esquerda | Banco **Aula BI** › schema **Loja** › tabela **Produtos** | Lista as colunas |
| 4 | Coluna `Id Produto` | Confira: Tipo semântico = **Chave de entidade** (Entity Key) | Já vem assim, porque é a PK no banco |
| 5 | Lista à esquerda | Tabela **Pedidos** | |
| 6 | Coluna `Id Produto` | Tipo semântico › **Chave estrangeira** (Foreign Key) | Surge um segundo campo, "Destino" |
| 7 | Destino | **Produtos → Id Produto** | Salva sozinho |
| 8 | Canto superior | **Sair do admin** (Exit admin) | |

### 5.3 Ver o relacionamento funcionando

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **+ Novo** › **Pergunta** › **Loja** › **Pedidos** | |
| 2 | [E] Resumir | **Contagem de linhas** · **+** **Soma de** `Quantidade` | |
| 3 | [E] Resumir | **Escolha uma coluna para agrupar** › agora aparece uma seção **Produto** (ou *Id Produto*) › `Categoria` ✅ | O Metabase faz a junção **sozinho** (junção implícita) |
| 4 | [E] | **Visualizar** › [G] botão **tabela** | |

| Categoria | Contagem | Soma de Quantidade |
|---|---|---|
| Eletrônicos | 11 | 19 |
| Informática | 13 | 25 |
| Móveis | 5 | 7 |
| *(vazio)* | 1 | 2 |

> 🧐 **O que é a linha vazia?** É o pedido 14, com o produto **P11**, que não existe em `produtos`. A junção implícita é uma **junção à esquerda**: mantém todos os pedidos, mesmo os sem produto.
>
> 🔗 **Outra vantagem da FK:** abra a tabela **Pedidos**, clique num valor de `Id Produto` (ex.: `P02`) › **Ver detalhes**. O Metabase abre o cadastro do produto.

### 5.4 Faturamento com Juntar dados + Coluna personalizada

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **+ Novo** › **Pergunta** › **Loja** › **Pedidos** | |
| 2 | [E] bloco Dados | Ícone **Juntar dados** (Join data) › **Produtos** | O Metabase sugere `Id Produto = Id Produto` por causa da FK |
| 3 | [E] Junção | Clique no ícone de tipo de junção › **Junção à esquerda** (Left join) | |
| 4 | [E] | Ícone **Coluna personalizada** › `[Quantidade] * [Produtos → Preco Unitario]` · Nome `Valor Total` › **Concluído** | Ao digitar `[Pre`, escolha na lista o `Preco Unitario` que vem **de Produtos** |
| 5 | [E] Resumir | **Soma de ...** › `Valor Total` · agrupar por `Produtos → Categoria` › **Visualizar** | |
| 6 | [D] | **Salvar** › `Faturamento por Categoria` | |

**Resultado esperado:**

| Categoria | Soma de Valor Total |
|---|---|
| Eletrônicos | R$ 24.190,00 |
| Informática | R$ 22.283,90 |
| Móveis | R$ 7.445,70 |
| *(vazio)* | *(vazio)* |
| **Total** | **R$ 53.919,60** |

**Por vendedor:** troque o agrupamento para `Vendedor`. O resultado é Paula **R$ 12.412,50**, Ricardo **R$ 19.833,20** e Sandra **R$ 21.673,90**.

**O mesmo em SQL:**

```sql
SELECT
    pr.categoria,
    count(*)                             AS qtd_pedidos,
    sum(pe.quantidade)                   AS itens,
    sum(pe.quantidade * pr.preco_unitario) AS faturamento
FROM loja.pedidos pe
LEFT JOIN loja.produtos pr ON pr.id_produto = pe.id_produto
GROUP BY pr.categoria
ORDER BY pr.categoria
```

> 🧪 **Experimento:** no passo 3, troque para **Junção interna** (Inner join). O pedido 14 **some**: ficam 29 pedidos e 51 itens.

### 5.5 Encontrar os problemas de integridade

**Produto que nunca foi vendido (P10)**

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | Nova pergunta | Dados = **Produtos** › **Juntar dados** › **Pedidos** (Junção à esquerda) | |
| 2 | [E] Filtro | `Pedidos → Id Pedido` › **Está vazio** (Is empty) › **Visualizar** | **P10 · Luminária de Mesa** |

**Pedido com produto inexistente (P11)**

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | Nova pergunta | Dados = **Pedidos** › **Juntar dados** › **Produtos** (Junção à esquerda) | |
| 2 | [E] Filtro | `Produtos → Id Produto` › **Está vazio** › **Visualizar** | **Pedido 14 · P11** |

```sql
-- Produtos sem venda
SELECT pr.id_produto, pr.produto
FROM loja.produtos pr
LEFT JOIN loja.pedidos pe ON pe.id_produto = pr.id_produto
WHERE pe.id_pedido IS NULL;

-- Pedidos com produto inexistente
SELECT pe.id_pedido, pe.id_produto
FROM loja.pedidos pe
LEFT JOIN loja.produtos pr ON pr.id_produto = pe.id_produto
WHERE pr.id_produto IS NULL;
```

### 5.6 Filtro de painel atravessando as tabelas

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | Painel `Aula BI` › editar (lápis) | **+** › adicione `Faturamento por Categoria` e uma pergunta "Soma de Quantidade por Vendedor" (feita em **Pedidos**) | |
| 2 | Topo | Ícone de **filtro** › **Texto ou categoria** › **É** | |
| 3 | Cartão "por Vendedor" | **Selecione…** › seção **Produto** › `Categoria` | Só é possível porque existe a FK: uma pergunta de **Pedidos** filtrada por uma coluna de **Produtos** |
| 4 | Topo | **Salvar** › escolha **Móveis** no filtro | A quantidade por vendedor é recalculada |

### 5.7 Chave estrangeira × Juntar dados

| | Chave estrangeira (Modelo de dados) | Juntar dados (na pergunta) |
|---|---|---|
| Onde configura | **Uma vez**, no Admin | Em **cada** pergunta |
| Quem usa | Todas as perguntas, painéis e filtros | Só aquela pergunta |
| Tipo de junção | Sempre à esquerda (implícita) | Você escolhe: esquerda, direita, interna, completa |
| Quando usar | **Padrão**: descreve o modelo do banco | Quando precisa de outra junção ou de uma tabela sem FK |

> 💬 **Comparação entre as ferramentas:**
>
> | Power BI | Tableau | Metabase |
> |---|---|---|
> | Relacionamento na Exibição de Modelo | Relacionamento ("linha") na Fonte de dados | Chave estrangeira no Modelo de dados |
> | Mesclar Consultas (Power Query) | Junção na camada física | Juntar dados / `JOIN` em SQL |
> | `RELATED(...)` | *(não tem: precisa de junção)* | `[Produtos → Coluna]` numa coluna personalizada |

---

## Apêndice: desligar o ambiente

```bash
docker compose down        # para os containers e mantém os dados e as perguntas do Metabase
docker compose down -v     # apaga tudo (banco e Metabase) para recomeçar do zero
```
