# ETL: dados limpos para os dashboards

O script [etl.py](etl.py) faz **em Python** a mesma limpeza que os passo a passos fazem à mão no Power BI, no Tableau e no Metabase. Ele grava os arquivos prontos em `dados_limpos/`, e com eles um dashboard novo é só **conectar e montar os gráficos**, sem nenhuma etapa de limpeza.

```
 PBI/*.csv (brutos) ──► Extract ──► Transform ─────────────────► Load ──► etl/dados_limpos/*.csv
                        (tudo como   (espaços, maiúsculas, tipos,           ├─ vendas.csv
                         texto)       duplicatas, nome/sobrenome,           ├─ consultas_nutricionista.csv
                                      horário início/fim, métricas)         ├─ produtos.csv
                                                                            ├─ pedidos.csv
                                                                            └─ relatorio_qualidade.csv
```

## Como rodar

Requisito: Python 3 com **pandas** (`py -m pip install pandas`).

```bash
py PBI/etl/etl.py
```

Saída esperada (resumo):

```
Load...
  vendas.csv                         300 linhas
  consultas_nutricionista.csv        221 linhas
  produtos.csv                        11 linhas
  pedidos.csv                         30 linhas
  relatorio_qualidade.csv             14 linhas

Resumo:
  Total de vendas ........ R$ 471,384.63
  Consultas .............. 221 (178 realizadas)
  Faturamento pedidos .... R$ 53,919.60
```

> Os CSVs brutos de vendas e consultas são gerados por [../gerar_dados.py](../gerar_dados.py), que usa uma semente fixa e por isso gera sempre os mesmos arquivos. Só é preciso rodá-lo de novo se quiser recriar os dados brutos.

## O que o ETL faz

| Arquivo | Transformações |
|---|---|
| **vendas** | espaços e maiúsculas/minúsculas em `cliente` e `categoria` · `uf` em maiúsculas · remove **5** linhas duplicadas · desconto vazio vira 0 · tipos (data, inteiro, decimal) · cria `primeiro_nome`, `sobrenome`, `cidade_uf`, `valor_bruto`, `valor_desconto`, `valor_liquido`, `ano`, `mes_numero`, `mes` |
| **consultas** | espaços e maiúsculas em `paciente` e `tipo_consulta` · remove **4** duplicadas · corrige `14h00` para `14:00` · divide `horario` em `horario_inicio` e `horario_fim` · cria `inicio_datahora`, `fim_datahora`, `duracao_min`, `turno`, `imc`, `realizada` (1 ou 0) |
| **produtos** | tipos · acrescenta o **P11** como `Produto não cadastrado` (categoria `Não informado`) · cria `qtd_pedidos` |
| **pedidos** | tipos · cria `valor_total` (quantidade × preço do produto) |

O arquivo `relatorio_qualidade.csv` lista cada problema encontrado e quantas linhas foram afetadas: duplicatas, vazios, o produto sem venda (P10), o pedido com produto inexistente (P11) etc. Ele é útil para uma página de "qualidade dos dados" no dashboard.

> 💡 **Por que o P11 entra em produtos?** Se o pedido 14 fosse apagado, o dado se perderia. Deixado como está, ele aparece como "(Em branco)" ou "Nulo". Com um registro "não cadastrado", o relacionamento fica íntegro e o problema continua **visível** no dashboard, com a categoria `Não informado`.

### Formato dos arquivos gerados

| Item | Formato |
|---|---|
| Separador | `;` |
| Decimal | vírgula (`3899,9`) |
| Datas | ISO: `2026-01-05` |
| Horas | `08:00:00` |
| Data e hora | `2026-03-02 08:00:00` |
| Codificação | UTF-8 com BOM (os acentos são reconhecidos automaticamente) |

---

## Novo dashboard no Power BI

As letras [A]…[K] são as áreas da tela descritas no [passo a passo do Power BI](../passo_a_passo_power_bi.md#parte-0-mapa-das-telas-onde-fica-cada-coisa).

### 1. Importar

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] Página Inicial | **Obter Dados** › **Texto/CSV** › `etl\dados_limpos\vendas.csv` | Pré-visualização |
| 2 | Pré-visualização | Delimitador = **Ponto e vírgula** › **Carregar** | Carrega direto, sem Power Query |
| 3 | [A] | Repita para `consultas_nutricionista.csv`, `produtos.csv`, `pedidos.csv` e `relatorio_qualidade.csv` | 5 tabelas em [F] |
| 4 | [B] **Tab** (Exibição de tabela) | Confira os tipos: datas com ícone de calendário, `horario_inicio` como **Hora** e valores como **Decimal** | Se algo vier como texto, ajuste em [A] **Ferramentas de coluna** › Tipo de dados |

### 2. Modelo

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [B] **Mod** | Confira a linha `produtos[id_produto]` **1 → \*** `pedidos[id_produto]` | Se não existir, arraste `id_produto` de uma tabela para a outra |
| 2 | [F] `vendas` › coluna `mes` | [A] **Ferramentas de coluna** › **Classificar por coluna** › `mes_numero` | Os meses ficam em ordem (Janeiro, Fevereiro…), e não em ordem alfabética |
| 3 | [F] `id_venda`, `id_consulta`, `id_pedido` | [A] Ferramentas de coluna › **Resumo** = **Não resumir** | Os IDs não são somados por engano |

> `vendas` e `consultas_nutricionista` são assuntos diferentes e **não** se relacionam. Cada uma alimenta a sua página.

### 3. Medidas

Como os dados já chegam limpos, as medidas ficam **simples**:

```dax
Total de Vendas     = SUM(vendas[valor_liquido])
Qtd de Vendas       = COUNTROWS(vendas)
Ticket Médio        = DIVIDE([Total de Vendas], [Qtd de Vendas])
Total de Descontos  = SUM(vendas[valor_desconto])

Total de Consultas  = COUNTROWS(consultas_nutricionista)
Consultas Realizadas = SUM(consultas_nutricionista[realizada])
Taxa de Ausência    = 1 - DIVIDE([Consultas Realizadas], [Total de Consultas])
Duração Média (min) = CALCULATE(AVERAGE(consultas_nutricionista[duracao_min]), consultas_nutricionista[realizada] = 1)

Faturamento Pedidos = SUM(pedidos[valor_total])
Qtd Pedidos         = COUNTROWS(pedidos)
```

### 4. Páginas sugeridas

| Página | Visuais |
|---|---|
| **Vendas** | Cartões `Total de Vendas`, `Qtd de Vendas`, `Ticket Médio` · Colunas por `categoria` · Linhas por `mes` · Barras top 10 por `cliente` · Mapa por `cidade_uf` · Segmentação `categoria` e `uf` |
| **Consultas** | Cartões `Total de Consultas`, `Consultas Realizadas`, `Taxa de Ausência` · Colunas empilhadas `nutricionista` × `status` · Rosca por `tipo_consulta` · Colunas por `turno` · Linha de `imc` médio por `data_consulta` |
| **Pedidos** | Colunas `Faturamento Pedidos` por `produtos[categoria]` · Barras por `vendedor` · Tabela `produtos[produto]` + `qtd_pedidos` |
| **Qualidade** | Tabela com `relatorio_qualidade` (tabela, etapa, linhas_afetadas) |

Para mudar de página, use as abas no rodapé de [C] e o botão **+** para criar uma página nova.

---

## Novo dashboard no Tableau

As letras [A]…[L] são as áreas da tela descritas no [passo a passo do Tableau](../passo_a_passo_tableau.md#parte-0-mapa-das-telas).

### 1. Conectar

São **3 fontes de dados**: uma para vendas, uma para consultas e uma para pedidos com produtos.

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | Conectar | **Arquivo de texto** › `etl\dados_limpos\vendas.csv` | |
| 2 | [K] | Seta **v** › **Propriedades do arquivo de texto** › `;` · UTF-8 · **Português (Brasil)** › **OK** | Decimais com vírgula lidos corretamente |
| 3 | [A] | **Dados** › **Nova fonte de dados** › `consultas_nutricionista.csv` (repita o passo 2) | |
| 4 | [A] | **Dados** › **Nova fonte de dados** › `produtos.csv` (repita o passo 2) | |
| 5 | [J] | Arraste `pedidos.csv` **ao lado** de `produtos.csv` › relacionamento `Id Produto` = `Id Produto` | Linha ("noodle") entre as duas |
| 6 | Seta **v** de `pedidos.csv` | Propriedades do arquivo de texto (como no passo 2) | |

> 💡 Agora **não precisa de junção** para o faturamento: o ETL já calculou `Valor Total` em `pedidos`.

### 2. Ajustes rápidos

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [C] | **Botão direito** em `Id Venda`, `Id Consulta`, `Id Pedido` › **Converter em dimensão** | IDs não são somados |
| 2 | [C] fonte consultas | Use `Inicio Datahora` / `Fim Datahora` para horários | O Tableau não tem tipo "só hora"; `Horario Inicio` chega como texto |
| 3 | [C] | **Botão direito** em `Valor Liquido` › **Propriedades padrão** › **Formato de número** › Moeda `R$` | |

### 3. Campos calculados

Como os dados chegam sem duplicatas, **não precisa** de expressões LOD:

```
Total de Vendas       = SUM([Valor Liquido])
Qtd de Vendas         = COUNTD([Id Venda])
Ticket Médio          = [Total de Vendas] / [Qtd de Vendas]

Total de Consultas    = COUNTD([Id Consulta])
Consultas Realizadas  = SUM([Realizada])
Taxa de Ausência      = 1 - [Consultas Realizadas] / [Total de Consultas]

Faturamento Pedidos   = SUM([Valor Total])
```

### 4. Planilhas e painel

| Planilha | Linhas / Colunas / Marcas |
|---|---|
| KPI Vendas | `Total de Vendas` em [H] Texto |
| Vendas por Categoria | Linhas `Categoria` · Colunas `Total de Vendas` · Mostre-me › barras |
| Vendas por Mês | Colunas `Data Venda` (seta **v** › **Mês**) · Linhas `Total de Vendas` › linha |
| Mapa | **Duplo clique** em `Cidade` (seta **v** › Função geográfica › Cidade) · Tamanho `Total de Vendas` |
| Consultas por Status | Colunas `Nutricionista` · Linhas `Total de Consultas` · Cor `Status` |
| Turno | Colunas `Turno` · Linhas `Consultas Realizadas` |
| Pedidos por Categoria | Linhas `Categoria` (produtos) · Colunas `Faturamento Pedidos` |

Depois, em [A] **Painel** › **Novo painel**, arraste as planilhas. Em cada gráfico, clique no ícone de **funil** (*Usar como filtro*) para que clicar numa barra filtre as outras planilhas.

---

## Valores para conferir

| Indicador | Valor |
|---|---|
| Vendas (linhas) | 300 |
| Total de vendas | R$ 471.384,63 |
| Por categoria | Eletrônicos R$ 166.540,71 · Informática R$ 183.316,02 · Móveis R$ 121.527,90 |
| Itens vendidos | 602 |
| Consultas | 221 (178 realizadas · 31 faltou · 12 cancelada) |
| Taxa de ausência | 19,5% |
| Consultas realizadas por nutricionista | André 62 · Camila 58 · Luiza 58 |
| Faturamento dos pedidos | R$ 53.919,60 |
| Categoria "Não informado" (pedido 14, P11) | 1 pedido, 2 itens, sem valor |
