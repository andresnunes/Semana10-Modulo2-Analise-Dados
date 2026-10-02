# Power BI: limpeza, transformação, agregação e relacionamento

Nesta aula usamos arquivos CSV que têm problemas colocados de propósito. Tudo é resolvido no **Power BI Desktop**: primeiro no Power Query (limpeza e transformação) e depois no modelo e nos visuais.

> Os mesmos exercícios também existem para o [Tableau](passo_a_passo_tableau.md) e para o [Metabase](passo_a_passo_metabase.md).

| Arquivo | Conteúdo | Objetivo principal |
|---|---|---|
| `vendas.csv` | Vendas com dados do cliente e do produto | **Primeiro nome** e **sobrenome** do cliente, **total de vendas** |
| `consultas_nutricionista.csv` | Agenda de consultas de nutricionistas | **Horário de início** e **horário de fim**, **contagem de consultas** |
| `Relacionamento/produtos.csv` | Cadastro de produtos (10 linhas) | Tabela **dimensão**, o lado "1" do relacionamento |
| `Relacionamento/pedidos.csv` | Pedidos, apenas com o `id_produto` (30 linhas) | Tabela **fato**, o lado "muitos" do relacionamento |

Todos os arquivos usam **`;`** como separador, **vírgula** como separador decimal, datas no formato **dd/mm/aaaa** e **UTF-8**.

### Fluxo geral da aula

```
 Obter Dados ──► Power Query ──► Fechar e ──► Exibição de ──► Medidas ──► Relatório
 (Texto/CSV)     (limpar e       Aplicar      Modelo           DAX         (visuais)
                  transformar)                (relacionamentos)
   Parte 1       Partes 2 e 3                  Parte 5         Parte 4    Partes 2-5
```

---

## Parte 0: Mapa das telas (onde fica cada coisa)

Nas tabelas de cliques, as letras entre colchetes (**[A]**, **[B]**…) indicam a área da tela.

### Tela principal do Power BI Desktop

```
+---------------------------------------------------------------------------------+
| [A] FAIXA DE OPÇÕES:  Arquivo | Página Inicial | Inserir | Modelagem | Exibir ... |
|     (Obter Dados, Transformar Dados, Nova Medida, Gerenciar Relações ficam aqui) |
+-----+-------------------------------------------+-----------+-------------------+
| [B] |                                           | [D]       | [E] VISUALIZAÇÕES |
|     |                                           | FILTROS   |  grade de ícones  |
| Rel |        [C] TELA DO RELATÓRIO              |           |  (cartão, colunas,|
|     |        (onde os visuais são desenhados)   |           |   tabela, mapa...)|
| Tab |                                           |           |  ---------------- |
|     |                                           |           |  "poços" de campos|
| Mod |                                           |           |  (Eixo X, Eixo Y, |
|     |                                           |           |   Campos, Legenda)|
|     |                                           |           +-------------------+
|     |                                           |           | [F] DADOS         |
|     +-------------------------------------------+           |  > vendas         |
|     |  Página 1  |  +                           |           |    cliente, uf... |
+-----+-------------------------------------------+-----------+-------------------+
 [B] Ícones da barra lateral:  Rel = Exibição de relatório
                               Tab = Exibição de tabela (ver os dados carregados)
                               Mod = Exibição de modelo (relacionamentos)
```

### Editor do Power Query (abre com "Transformar Dados")

```
+---------------------------------------------------------------------------------+
| [G] FAIXA: Arquivo | Página Inicial | Transformar | Adicionar Coluna | Exibição   |
+---------------------------------------------------------------------------------+
| [H] BARRA DE FÓRMULAS:  fx  = Table.TransformColumns(...)                       |
|     (se não aparecer: Exibição > marcar "Barra de Fórmulas")                    |
+----------------+-------------------------------------------+--------------------+
| [I] CONSULTAS  | [J] GRADE DE DADOS                        | [K] CONFIGURAÇÕES  |
|                |                                           |     DA CONSULTA    |
|  vendas        | ABC cliente  v | 1.2 preco_unitario v |  |  Propriedades:     |
|  consultas_... | Ana Paula ...  | 3899,9               |  |   Nome: vendas     |
|                | carlos edu...  | 89,9                 |  |  Etapas Aplicadas: |
|  (botão dir.   |                                           |   Fonte            |
|   = Referência,|  * clique no cabeçalho  = seleciona       |   Cabeçalhos Prom. |
|   Duplicar,    |  * Ctrl + clique         = várias colunas |   Tipo Alterado    |
|   Renomear)    |  * ícone ABC/123/1.2     = trocar tipo    |   (X apaga etapa)  |
|                |  * seta  v               = filtro         |                    |
|                |  * botão direito         = menu da coluna |                    |
+----------------+-------------------------------------------+--------------------+
```

---

## Parte 1: Importar os arquivos

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] Página Inicial | **Obter Dados** › **Texto/CSV** | Abre o explorador de arquivos |
| 2 | Explorador | Selecione `PBI\vendas.csv` › **Abrir** | Abre a janela de pré-visualização |
| 3 | Pré-visualização | **Origem do Arquivo** = `65001: Unicode (UTF-8)` | Acentos corretos (`Florianópolis`) |
| 4 | Pré-visualização | **Delimitador** = `Ponto e vírgula` | As colunas se separam |
| 5 | Pré-visualização (rodapé) | **Transformar Dados** (e **não** em Carregar) | Abre o Power Query |
| 6 | [G] Página Inicial | **Nova Fonte** › **Texto/CSV** › `consultas_nutricionista.csv` › **OK** | A segunda consulta aparece em [I] |

> 💡 Mostre o painel **[K] Etapas Aplicadas**. Cada clique vira uma etapa: clicar numa etapa "volta no tempo", e o **X** apaga a etapa.

---

## Parte 2: Vendas

Em **[I] Consultas**, clique em **`vendas`**.

### 2.1 Limpar os textos

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [J] cabeçalho | Clique em **`cliente`**, depois **Ctrl** + clique em **`categoria`** | As duas colunas ficam selecionadas (verde) |
| 2 | [G] Transformar | **Formato** › **Cortar** | Tira os espaços do começo e do fim |
| 3 | [G] Transformar | **Formato** › **Colocar Cada Palavra Em Maiúscula** | `JOÃO PEDRO ALMEIDA` passa a `João Pedro Almeida`, `MÓVEIS` passa a `Móveis` |
| 4 | [J] cabeçalho | Clique em **`uf`** | Seleciona só a UF |
| 5 | [G] Transformar | **Formato** › **MAIÚSCULAS** | `sc` passa a `SC` |

> 🔎 **Demonstração:** clique na seta **v** da coluna `categoria` antes e depois. Antes aparecem 9 valores, depois só 3.

### 2.2 Tipos de dados

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [J] ícone à esquerda do cabeçalho `id_venda` | **Número Inteiro** | Ícone `123` |
| 2 | [J] ícone de `data_venda` | **Data** | Ícone de calendário |
| 3 | [J] ícone de `quantidade` | **Número Inteiro** | |
| 4 | [J] ícone de `preco_unitario` e de `desconto_pct` | **Número Decimal** | Ícone `1.2` |

> ⚠️ Se o Power BI estiver em inglês, `3899,90` pode virar `389990`. Corrija assim: [J] **botão direito** no cabeçalho › **Alterar Tipo** › **Usando a Localidade...** › Tipo = *Número Decimal*, Localidade = *Português (Brasil)* › **OK**.

### 2.3 Remover duplicatas e tratar vazios

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [J] canto superior esquerdo da grade (ícone de tabela) | **Remover Duplicatas** | 305 linhas passam a **300** (saem 5 vendas repetidas, como a `1010`) |
| 2 | [J] cabeçalho | Clique em **`desconto_pct`** | |
| 3 | [G] Transformar | **Substituir Valores** | Abre a caixa de diálogo |
| 4 | Diálogo | Valor a Localizar = `null`, Substituir Por = `0` › **OK** | Os vazios viram 0 |

> 💡 A contagem de linhas aparece no **rodapé** do Power Query (canto inferior esquerdo), por exemplo "11 COLUNAS, 300 LINHAS".

### 2.4 ⭐ Primeiro nome e sobrenome

O primeiro nome é a **primeira palavra** e o sobrenome é a **última palavra**. Isso funciona também para nomes compostos, como `Ana Paula Ribeiro`.

**Primeiro nome**

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [J] cabeçalho | Clique em **`cliente`** | |
| 2 | [G] Adicionar Coluna | **Extrair** › **Texto Antes do Delimitador** | Abre o diálogo |
| 3 | Diálogo | Delimitador = ` ` (**um espaço**) › **OK** | Nova coluna `Texto Antes do Delimitador` no fim da grade |
| 4 | [J] cabeçalho novo | **Duplo clique** › digite `primeiro_nome` › **Enter** | Coluna renomeada |

**Sobrenome**

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [J] cabeçalho | Clique em **`cliente`** | |
| 2 | [G] Adicionar Coluna | **Extrair** › **Texto Após o Delimitador** | Abre o diálogo |
| 3 | Diálogo | Delimitador = ` ` (espaço) › abra **Opções avançadas** | |
| 4 | Diálogo | *Examinar em busca do delimitador* = **Do final da entrada** › **OK** | Pega a última palavra |
| 5 | [J] cabeçalho novo | **Duplo clique** › `sobrenome` › **Enter** | |

| cliente | primeiro_nome | sobrenome |
|---|---|---|
| Ana Paula Ribeiro | Ana | Ribeiro |
| Beatriz Santos | Beatriz | Santos |
| Marcos Vinícius Teixeira | Marcos | Teixeira |

> 🧪 **Outras formas de fazer:**
> - [G] Transformar › **Dividir Coluna** › **Por Delimitador** › *Delimitador mais à esquerda*. Essa opção **substitui** a coluna original, enquanto *Adicionar Coluna* mantém a original.
> - [G] Adicionar Coluna › **Coluna de Exemplos** › **De Seleção**: digite `Ana` na 1ª linha e `Carlos` na 2ª, dê **Enter** e o Power BI descobre a regra sozinho.

### 2.5 Juntar colunas (Mesclar)

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [J] cabeçalho | Clique em **`cidade`**, depois **Ctrl** + clique em **`uf`** | A ordem dos cliques define a ordem do texto |
| 2 | [G] Adicionar Coluna | **Mesclar Colunas** | Abre o diálogo |
| 3 | Diálogo | Separador = **Personalizado** › digite ` - ` | |
| 4 | Diálogo | Novo nome da coluna = `cidade_uf` › **OK** | `Florianópolis - SC` |

### 2.6 Colunas calculadas

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [G] Adicionar Coluna | **Coluna Personalizada** | Abre o editor de fórmula |
| 2 | Diálogo | Nome = `valor_bruto`, fórmula `[quantidade] * [preco_unitario]` › **OK** | (Dê duplo clique nas colunas da lista da direita para inseri-las) |
| 3 | [G] Adicionar Coluna | **Coluna Personalizada** | |
| 4 | Diálogo | Nome = `valor_liquido`, fórmula `[valor_bruto] * (1 - [desconto_pct] / 100)` › **OK** | |
| 5 | [J] ícone `ABC123` das duas colunas novas | **Número Decimal** | |
| 6 | [J] cabeçalho `data_venda` › [G] Adicionar Coluna | **Data** › **Mês** › **Nome do Mês** | Coluna com `janeiro`, `fevereiro`… |

### 2.7 ⭐ Agregação (Agrupar Por)

Para não perder a tabela detalhada, o agrupamento é feito numa **cópia vinculada** (Referência).

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [I] Consultas | **Botão direito** em `vendas` › **Referência** | Aparece `vendas (2)` |
| 2 | [K] Propriedades › Nome | Digite `vendas_por_categoria` | |
| 3 | [G] Transformar | **Agrupar Por** | Abre o diálogo |
| 4 | Diálogo | Marque **Avançado** | Permite várias colunas de agregação |
| 5 | Diálogo | Agrupar por = `categoria` | |
| 6 | Diálogo | Preencha a 1ª agregação e clique em **Adicionar agregação** para cada uma das próximas (tabela abaixo) › **OK** | A tabela fica com 3 linhas |

| Nome da nova coluna | Operação | Coluna |
|---|---|---|
| `qtd_vendas` | Contar Linhas | |
| `itens_vendidos` | Soma | `quantidade` |
| `faturamento` | Soma | `valor_liquido` |
| `ticket_medio` | Média | `valor_liquido` |

**Resultado esperado:**

| categoria | qtd_vendas | faturamento |
|---|---|---|
| Eletrônicos | 88 | 166.540,71 |
| Informática | 114 | 183.316,02 |
| Móveis | 98 | 121.527,90 |

**Exercício:** crie `vendas_por_cliente`, agrupando por `primeiro_nome` + `sobrenome` (use **Adicionar agrupamento**), e descubra quem mais comprou.

### 2.8 ⭐ Total de vendas

O total de vendas é a **soma de `valor_liquido`**. Para os dados deste exercício, o valor esperado é **R$ 471.384,63** (300 vendas, 602 itens).

Há três formas de chegar nele, da mais rápida para a mais recomendada.

**Forma A: soma direto no visual (agregação implícita)**

Antes, clique em [G] Página Inicial › **Fechar e Aplicar**.

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [E] Visualizações | Ícone **Cartão** | Um cartão vazio aparece em [C] |
| 2 | [F] Dados › `vendas` | **Arraste** `valor_liquido` para o poço **Campos** do cartão | O cartão mostra `37,51 mil` |
| 3 | [E] poço Campos | Seta **v** ao lado de `valor_liquido` | Mostra que está em **Soma**; troque para Média, Mínimo… para ver a diferença |

**Forma B: medida DAX (a recomendada)**

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [F] Dados | **Botão direito** na tabela `vendas` › **Nova medida** | A barra de fórmulas abre no topo |
| 2 | Barra de fórmulas | Digite a fórmula abaixo › **Enter** (ou ✔) | Aparece `Total de Vendas` com ícone de calculadora em [F] |
| 3 | [F] Dados | Selecione a medida › [A] **Ferramentas de medida** › Formato = **Moeda** | Exibe `R$ 471.384,63` |
| 4 | [E] | Novo **Cartão** › arraste `Total de Vendas` | |

```dax
Total de Vendas = SUM(vendas[valor_liquido])
```

Outras variações para mostrar:

```dax
Total Bruto = SUMX(vendas, vendas[quantidade] * vendas[preco_unitario])

Total de Descontos = [Total Bruto] - [Total de Vendas]

Qtd de Vendas = DISTINCTCOUNT(vendas[id_venda])

Itens Vendidos = SUM(vendas[quantidade])
```

> 💬 `SUM` soma uma coluna que já existe. `SUMX` calcula linha a linha (quantidade × preço) e soma o resultado, sem precisar criar a coluna antes.

**Forma C: no Power Query (Estatísticas)**

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] Página Inicial | **Transformar Dados** | Volta ao Power Query |
| 2 | [I] | **Botão direito** em `vendas` › **Referência** › renomeie para `total_vendas` | |
| 3 | [J] | Clique em **`valor_liquido`** | |
| 4 | [G] Transformar | **Estatísticas** › **Soma** | A consulta vira **um único número**: `471384,628` |

> ⚠️ A forma C gera um número fixo: ele **não muda** com filtros e segmentações do relatório. Use a forma C só para comparar. No relatório, prefira a medida (forma B).

**Demonstração com segmentação:** em [E], adicione uma **Segmentação de dados** com `categoria`. Clique em "Móveis" e veja o cartão da medida mudar para **R$ 121.527,90**.

---

## Parte 3: Consultas de nutricionista

Volte ao Power Query ([A] Página Inicial › **Transformar Dados**) e, em **[I]**, clique em **`consultas_nutricionista`**.

### 3.1 Limpar os textos

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [J] | Clique em **`paciente`** + **Ctrl** + clique em **`tipo_consulta`** | |
| 2 | [G] Transformar | **Formato** › **Cortar** | |
| 3 | [G] Transformar | **Formato** › **Colocar Cada Palavra Em Maiúscula** | `RETORNO` e `retorno` passam a `Retorno` |
| 4 | [J] canto superior esquerdo da grade | **Remover Duplicatas** | 225 linhas passam a **221** (saem 4 consultas repetidas) |

### 3.2 Padronizar o horário

Os horários `14h00 - 14h50` precisam virar `14:00 - 14:50`.

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [J] | Clique **somente** em **`horario`** | |
| 2 | [G] Transformar | **Substituir Valores** | |
| 3 | Diálogo | Localizar = `h`, Substituir Por = `:` › **OK** | `14h00` passa a `14:00` |

> ⚠️ Deixe só a coluna `horario` selecionada. Com outras colunas selecionadas, o `h` de "Martins" ou "Helena" também seria trocado!

### 3.3 ⭐ Horário de início e horário de fim

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [J] | Clique em **`horario`** | |
| 2 | [G] Transformar | **Dividir Coluna** › **Por Delimitador** | Abre o diálogo |
| 3 | Diálogo | Delimitador = **--Personalizado--** › digite `-` | |
| 4 | Diálogo | Dividir em = **Cada ocorrência do delimitador** › **OK** | Surgem `horario.1` e `horario.2` |
| 5 | [J] | **Duplo clique** em `horario.1` › `horario_inicio`; em `horario.2` › `horario_fim` | |
| 6 | [J] | Selecione as duas (**Ctrl**) › [G] Transformar › **Formato** › **Cortar** | Tira o espaço de `08:00 ` e ` 08:50` |
| 7 | [J] ícone `ABC` das duas | **Hora** | Ícone de relógio |

| horario (antes) | horario_inicio | horario_fim |
|---|---|---|
| `08:00 - 08:50` | 08:00:00 | 08:50:00 |
| `9:00-9:50` | 09:00:00 | 09:50:00 |
| `14h00 - 14h50` | 14:00:00 | 14:50:00 |

### 3.4 Tipos das demais colunas

| Coluna | Clique no ícone do cabeçalho e escolha |
|---|---|
| `id_consulta` | Número Inteiro |
| `data_consulta` | Data |
| `peso_kg`, `altura_m`, `valor` | Número Decimal |

As consultas com status `Faltou` ou `Cancelada` ficam com `null` no peso e na altura. Isso está **correto**, porque não houve medição.

### 3.5 Colunas derivadas do horário

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [G] Adicionar Coluna | **Coluna Personalizada** › Nome `duracao_min` › fórmula `Duration.TotalMinutes([horario_fim] - [horario_inicio])` › **OK** | Duração em minutos (50, 30…) |
| 2 | [G] Adicionar Coluna | **Coluna Personalizada** › Nome `inicio_datahora` › fórmula `[data_consulta] & [horario_inicio]` › **OK** | Data e hora juntas; mude o tipo para **Data/Hora** |
| 3 | [G] Adicionar Coluna | **Coluna Condicional** | Abre o assistente "Se… então… senão" |
| 4 | Diálogo | Nome `turno` · Nome da Coluna = `horario_inicio` · Operador = **é menor que** · Valor = `12:00` · Saída = `Manhã` · Senão = `Tarde` › **OK** | |
| 5 | [G] Adicionar Coluna | **Coluna Personalizada** › Nome `imc` › fórmula abaixo › **OK** | IMC com 1 casa decimal |

```
if [peso_kg] = null then null else Number.Round([peso_kg] / ([altura_m] * [altura_m]), 1)
```

> 🖱️ **Duração só com cliques:** clique em `horario_fim`, depois **Ctrl** + clique em `horario_inicio`, e vá em [G] Adicionar Coluna › **Hora** › **Subtrair**. O resultado é do tipo *Duração*. Depois use [G] Transformar › **Duração** › **Total de Minutos**.

### 3.6 ⭐ Agregação por nutricionista

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [I] | **Botão direito** em `consultas_nutricionista` › **Referência** › renomeie para `resumo_nutricionista` | |
| 2 | [J] | Seta **v** de `status` › desmarque tudo menos **Realizada** › **OK** | Ficam **178 linhas** |
| 3 | [G] Transformar | **Agrupar Por** › **Avançado** › Agrupar por = `nutricionista` | |
| 4 | Diálogo | Crie as agregações abaixo com **Adicionar agregação** › **OK** | 3 linhas: André **62**, Camila **58** e Luiza **58** consultas |

| Nome | Operação | Coluna |
|---|---|---|
| `consultas` | Contar Linhas | |
| `faturamento` | Soma | `valor` |
| `duracao_media_min` | Média | `duracao_min` |
| `minutos_atendidos` | Soma | `duracao_min` |

**Exercício:** agrupe por `nutricionista` **e** `tipo_consulta` (**Adicionar agrupamento**).

### 3.7 ⭐ Contagem de consultas

Valores esperados: **221 consultas no total**, sendo **178 Realizadas**, **31 Faltou** e **12 Cancelada**.

**Forma A: contagem direto no visual**

Antes, clique em [G] Página Inicial › **Fechar e Aplicar**.

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [E] Visualizações | **Cartão** | |
| 2 | [F] Dados › `consultas_nutricionista` | Arraste **`id_consulta`** para **Campos** | ⚠️ Mostra **24.531**, porque o Power BI **somou** os IDs! |
| 3 | [E] poço Campos | Seta **v** em `id_consulta` › **Contagem** | Agora mostra **221** ✅ |

> 💬 **Ponto importante para a turma:** colunas numéricas vêm com **Soma** por padrão, mesmo quando somar não faz sentido (IDs, códigos, CPF). Para não repetir o erro, selecione `id_consulta` em [F] e, em [A] **Ferramentas de coluna** › **Resumo**, escolha **Não resumir**.

**Forma B: medidas DAX**

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [F] Dados | **Botão direito** em `consultas_nutricionista` › **Nova medida** | |
| 2 | Barra de fórmulas | Digite cada medida abaixo › **Enter** (repita o passo 1 para cada medida) | |
| 3 | [E] | Um **Cartão** para cada medida | 221 / 178 / 43 / 19,5% |

```dax
Total de Consultas = COUNTROWS(consultas_nutricionista)

Consultas Realizadas =
CALCULATE([Total de Consultas], consultas_nutricionista[status] = "Realizada")

Ausências =
CALCULATE([Total de Consultas], consultas_nutricionista[status] IN {"Faltou", "Cancelada"})

Taxa de Ausência = DIVIDE([Ausências], [Total de Consultas])

Pacientes Atendidos =
CALCULATE(DISTINCTCOUNT(consultas_nutricionista[paciente]), consultas_nutricionista[status] = "Realizada")
```

Formate `Taxa de Ausência` como **Porcentagem**: [A] Ferramentas de medida › botão **%**.

**Visual de contagem por status**

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [E] | **Gráfico de colunas clusterizado** | |
| 2 | [F] | Arraste `status` para o **Eixo X** e `Total de Consultas` para o **Eixo Y** | Realizada 178, Faltou 31, Cancelada 12 |
| 3 | [F] | Arraste `nutricionista` para a **Legenda** | Colunas separadas por nutricionista |

**Forma C: no Power Query.** Crie uma **Referência** da consulta › [G] Transformar › **Agrupar Por** `status` › Operação **Contar Linhas**. O resultado é uma tabela fixa com 3 linhas.

**Contagem por tipo (somente realizadas):** Retorno **137**, Primeira Consulta **21**, Avaliação Esportiva **20**.

---

## Parte 4: Relatório (juntando tudo)

```dax
Ticket Médio = DIVIDE([Total de Vendas], [Qtd de Vendas])

Duração Média (min) =
CALCULATE(AVERAGE(consultas_nutricionista[duracao_min]), consultas_nutricionista[status] = "Realizada")
```

| Visual ([E]) | Campos (arrastar de [F]) |
|---|---|
| Cartão | `Total de Vendas`, `Ticket Médio`, `Total de Consultas`, `Taxa de Ausência` |
| Gráfico de colunas | Eixo X `categoria`, Eixo Y `Total de Vendas` |
| Gráfico de barras | Eixo Y `primeiro_nome`, Eixo X `Total de Vendas` (top clientes) |
| Mapa | Local `cidade_uf`, Tamanho da bolha `Total de Vendas` |
| Gráfico de linhas | Eixo X `data_venda`, Eixo Y `Total de Vendas` |
| Colunas empilhadas | Eixo X `nutricionista`, Legenda `turno`, Eixo Y `Consultas Realizadas` |
| Rosca | Legenda `status`, Valores `Total de Consultas` |
| Segmentação | `data_consulta`, `tipo_consulta`, `categoria` |

> 💬 **Para discutir com a turma:** o *Agrupar Por* (Power Query) gera uma tabela **fixa**, já resumida. A medida DAX é **recalculada** a cada filtro e segmentação.

---

## Parte 5: ⭐ Relacionamento entre tabelas

Aqui temos **duas tabelas separadas**:

```
        produtos  (dimensão)                        pedidos  (fato)
  +---------------------------+              +---------------------------+
  | id_produto  (chave)   [1] |------------<*| id_produto                |
  | produto                   |   1 : muitos | id_pedido                 |
  | categoria                 |              | data_pedido               |
  | marca                     |   filtro --> | quantidade                |
  | preco_unitario            |              | vendedor                  |
  +---------------------------+              +---------------------------+
   10 linhas, 1 por produto                   30 linhas, o mesmo produto
                                               aparece várias vezes
```

- A tabela `pedidos` **não tem** o nome, a categoria nem o preço, só o `id_produto`.
- Para saber "quanto vendemos por categoria", o Power BI precisa **ligar** as duas tabelas.
- Há duas "armadilhas" nos dados, colocadas de propósito:
  - o produto **P10** (Luminária) **nunca foi vendido**;
  - o pedido **14** usa o **P11**, que **não existe** no cadastro.

> 📁 Use um **arquivo novo** do Power BI (Arquivo › Novo) para este exemplo.

### 5.1 Importar as duas tabelas

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] Página Inicial | **Obter Dados** › **Texto/CSV** › `Relacionamento\produtos.csv` | |
| 2 | Pré-visualização | Delimitador = **Ponto e vírgula** › **Carregar** | Os dados já estão limpos, não precisa de Power Query |
| 3 | [A] Página Inicial | **Obter Dados** › **Texto/CSV** › `Relacionamento\pedidos.csv` › **Carregar** | |
| 4 | [B] | Ícone **Tab** (Exibição de tabela) › clique em cada tabela em [F] | Confira: `preco_unitario` como Decimal e `data_pedido` como Data |

### 5.2 Primeiro, SEM relacionamento (para ver o problema)

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [B] | Ícone **Mod** (Exibição de modelo) | Duas caixas, uma para cada tabela |
| 2 | Tela do modelo | Se já existir uma **linha** ligando as tabelas: **botão direito** na linha › **Excluir** › **Sim** | O Power BI pode ter criado o relacionamento sozinho, porque as colunas têm o mesmo nome |
| 3 | [B] | Ícone **Rel** (Exibição de relatório) | |
| 4 | [E] | **Tabela** (ícone de grade) | |
| 5 | [F] | Arraste `produtos[categoria]` e depois `pedidos[quantidade]` | ❌ **Todas as categorias mostram 53**, o total geral |

> 💬 Sem relacionamento, o Power BI **não sabe** qual pedido pertence a qual categoria, então repete o total em todas as linhas.

### 5.3 Criar o relacionamento

**Jeito 1: arrastar (o mais visual)**

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [B] | Ícone **Mod** | |
| 2 | Caixa `produtos` | **Arraste** o campo `id_produto` e **solte** sobre `id_produto` da caixa `pedidos` | Abre o diálogo *Novo relacionamento* |
| 3 | Diálogo | Confira: Cardinalidade = **Muitos para um (\*:1)** · Direção do filtro cruzado = **Único** · ☑ **Ativar este relacionamento** › **Salvar/OK** | Aparece uma linha com **1** do lado `produtos` e **\*** do lado `pedidos` |

**Jeito 2: pelo menu**

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] Página Inicial (ou Modelagem) | **Gerenciar Relações** › **Novo...** | |
| 2 | Diálogo | Tabela de cima = `pedidos`, clique na coluna `id_produto` · Tabela de baixo = `produtos`, clique em `id_produto` | As colunas selecionadas ficam destacadas |
| 3 | Diálogo | Cardinalidade **Muitos para um** › **OK** › **Fechar** | |

> 🔍 **Para inspecionar:** dê **duplo clique na linha** do relacionamento para reabrir as configurações. Passe o mouse sobre a linha para ver as colunas ligadas destacadas.

### 5.4 Ver o relacionamento funcionando

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [B] | Ícone **Rel** | A tabela da etapa 5.2 **se corrige sozinha** |
| 2 | Tabela visual | Observe os valores | Informática **25**, Eletrônicos **19**, Móveis **7**, **(Em branco) 2** |

> 🧐 **O que é "(Em branco)"?** É o pedido 14, com o produto **P11**, que não existe em `produtos`. O Power BI não descarta a linha, mas também não sabe a categoria dela. Na prática, isso indica que o **cadastro está incompleto**, e é um ótimo gancho para falar de qualidade de dados.

### 5.5 Coluna calculada com RELATED

`RELATED` "busca" um valor na tabela do lado **1**, seguindo o relacionamento (parecido com o PROCV do Excel).

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [F] | **Botão direito** em `pedidos` › **Nova coluna** | |
| 2 | Barra de fórmulas | `preco = RELATED(produtos[preco_unitario])` › **Enter** | Cada pedido ganha o preço do produto |
| 3 | [F] | **Botão direito** em `pedidos` › **Nova coluna** | |
| 4 | Barra de fórmulas | `valor_total = pedidos[quantidade] * pedidos[preco]` › **Enter** | |
| 5 | [B] | Ícone **Tab** › tabela `pedidos` | Veja as colunas novas; o pedido 14 (P11) fica **vazio** |

> ⚠️ Faça o teste: exclua o relacionamento e a coluna `preco` dá **erro**. O `RELATED` só funciona se o relacionamento existir.

### 5.6 Medidas usando as duas tabelas

[F] › **Botão direito** em `pedidos` › **Nova medida**, para cada uma:

```dax
Faturamento Pedidos = SUMX(pedidos, pedidos[quantidade] * RELATED(produtos[preco_unitario]))

Qtd Pedidos = COUNTROWS(pedidos)

Itens Vendidos = SUM(pedidos[quantidade])

Qtd Pedidos (com zero) = COUNTROWS(pedidos) + 0

Produtos Sem Venda = COUNTROWS(FILTER(produtos, ISEMPTY(RELATEDTABLE(pedidos))))
```

**Resultado esperado:**

| categoria | Qtd Pedidos | Itens Vendidos | Faturamento Pedidos |
|---|---|---|---|
| Eletrônicos | 11 | 19 | R$ 24.190,00 |
| Informática | 13 | 25 | R$ 22.283,90 |
| Móveis | 5 | 7 | R$ 7.445,70 |
| (Em branco) | 1 | 2 | *(vazio)* |
| **Total** | **30** | **53** | **R$ 53.919,60** |

| vendedor | Faturamento Pedidos |
|---|---|
| Paula | R$ 12.412,50 |
| Ricardo | R$ 19.833,20 |
| Sandra | R$ 21.673,90 |

`Produtos Sem Venda` = **1** (o P10, Luminária de Mesa).

### 5.7 Visuais para demonstrar o filtro atravessando as tabelas

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [E] | **Segmentação de dados** › arraste `produtos[categoria]` | |
| 2 | [E] | **Gráfico de colunas** › Eixo X `pedidos[vendedor]` › Eixo Y `Faturamento Pedidos` | |
| 3 | [E] | **Tabela** › `produtos[produto]` + `Qtd Pedidos (com zero)` | O P10 aparece com **0** (com `Qtd Pedidos`, ele sumiria) |
| 4 | Segmentação | Clique em **Móveis** | O gráfico de **vendedor** (coluna de `pedidos`) é filtrado por um campo de `produtos`. Isso é o relacionamento funcionando! |
| 5 | Gráfico de colunas | Clique na coluna **Paula** | A tabela de produtos é filtrada? **Não**, porque a direção do filtro é **Único** (vai de `produtos` para `pedidos`) |

> 🧪 **Experimento:** na Exibição de modelo, dê **duplo clique** na linha › Direção do filtro cruzado = **Ambas** › **OK**. Repita o passo 5: agora a tabela de produtos é filtrada. Explique que **Único** é o padrão recomendado, e que **Ambas** deve ser usado com cuidado, porque pode deixar o modelo ambíguo e lento.

### 5.8 Relacionamento × Mesclar Consultas

Também é possível **juntar** as tabelas no Power Query, trazendo as colunas de `produtos` para dentro de `pedidos`:

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **Transformar Dados** › [I] clique em `pedidos` | |
| 2 | [G] Página Inicial | **Mesclar Consultas** › **Mesclar Consultas como Nova** | |
| 3 | Diálogo | Tabela de cima `pedidos`, clique em `id_produto` · Tabela de baixo `produtos`, clique em `id_produto` · Tipo de Junção = **Externa esquerda** › **OK** | Surge uma coluna `produtos` com "Table" |
| 4 | [J] | Ícone **⇔** no cabeçalho da coluna `produtos` › marque `produto`, `categoria`, `preco_unitario` › **OK** | As colunas ficam todas numa tabela só |

| | Relacionamento (Modelo) | Mesclar (Power Query) |
|---|---|---|
| Tabelas | Continuam separadas | Viram uma tabela só |
| Tamanho | Menor (a categoria é guardada 1 vez) | Maior (repete a categoria em cada pedido) |
| Quando usar | **Padrão para modelagem** (esquema estrela) | Quando precisa de uma tabela única e plana |

---

## Apêndice: código M completo (Editor Avançado)

Para conferir o resultado, ou montar tudo de uma vez: [G] Página Inicial › **Editor Avançado**. Troque `C:\CAMINHO` pelo caminho da sua máquina.

### vendas
```powerquery
let
    Fonte = Csv.Document(File.Contents("C:\CAMINHO\PBI\vendas.csv"), [Delimiter=";", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
    TextoLimpo = Table.TransformColumns(Cabecalhos, {
        {"cliente", each Text.Proper(Text.Trim(_)), type text},
        {"categoria", each Text.Proper(Text.Trim(_)), type text},
        {"uf", each Text.Upper(Text.Trim(_)), type text}}),
    Tipos = Table.TransformColumnTypes(TextoLimpo, {
        {"id_venda", Int64.Type}, {"data_venda", type date}, {"quantidade", Int64.Type},
        {"preco_unitario", type number}, {"desconto_pct", type number}}, "pt-BR"),
    SemDuplicatas = Table.Distinct(Tipos),
    DescontoZero = Table.ReplaceValue(SemDuplicatas, null, 0, Replacer.ReplaceValue, {"desconto_pct"}),
    PrimeiroNome = Table.AddColumn(DescontoZero, "primeiro_nome", each Text.BeforeDelimiter([cliente], " "), type text),
    Sobrenome = Table.AddColumn(PrimeiroNome, "sobrenome", each Text.AfterDelimiter([cliente], " ", {0, RelativePosition.FromEnd}), type text),
    CidadeUF = Table.AddColumn(Sobrenome, "cidade_uf", each [cidade] & " - " & [uf], type text),
    ValorBruto = Table.AddColumn(CidadeUF, "valor_bruto", each [quantidade] * [preco_unitario], type number),
    ValorLiquido = Table.AddColumn(ValorBruto, "valor_liquido", each [valor_bruto] * (1 - [desconto_pct] / 100), type number),
    Mes = Table.AddColumn(ValorLiquido, "mes", each Date.MonthName([data_venda], "pt-BR"), type text)
in
    Mes
```

### vendas_por_categoria
```powerquery
let
    Fonte = vendas,
    Agrupado = Table.Group(Fonte, {"categoria"}, {
        {"qtd_vendas", each Table.RowCount(_), Int64.Type},
        {"itens_vendidos", each List.Sum([quantidade]), type number},
        {"faturamento", each List.Sum([valor_liquido]), type number},
        {"ticket_medio", each List.Average([valor_liquido]), type number}})
in
    Agrupado
```

### total_vendas
```powerquery
let
    Fonte = vendas,
    Total = List.Sum(Fonte[valor_liquido])
in
    Total
```

### consultas_nutricionista
```powerquery
let
    Fonte = Csv.Document(File.Contents("C:\CAMINHO\PBI\consultas_nutricionista.csv"), [Delimiter=";", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
    TextoLimpo = Table.TransformColumns(Cabecalhos, {
        {"paciente", each Text.Proper(Text.Trim(_)), type text},
        {"tipo_consulta", each Text.Proper(Text.Trim(_)), type text}}),
    SemDuplicatas = Table.Distinct(TextoLimpo),
    HoraPadrao = Table.ReplaceValue(SemDuplicatas, "h", ":", Replacer.ReplaceText, {"horario"}),
    DividirHorario = Table.SplitColumn(HoraPadrao, "horario", Splitter.SplitTextByDelimiter("-", QuoteStyle.None), {"horario_inicio", "horario_fim"}),
    AparaHorarios = Table.TransformColumns(DividirHorario, {{"horario_inicio", Text.Trim, type text}, {"horario_fim", Text.Trim, type text}}),
    Tipos = Table.TransformColumnTypes(AparaHorarios, {
        {"id_consulta", Int64.Type}, {"data_consulta", type date},
        {"horario_inicio", type time}, {"horario_fim", type time},
        {"peso_kg", type number}, {"altura_m", type number}, {"valor", type number}}, "pt-BR"),
    Duracao = Table.AddColumn(Tipos, "duracao_min", each Duration.TotalMinutes([horario_fim] - [horario_inicio]), Int64.Type),
    InicioDataHora = Table.AddColumn(Duracao, "inicio_datahora", each [data_consulta] & [horario_inicio], type datetime),
    Turno = Table.AddColumn(InicioDataHora, "turno", each if [horario_inicio] < #time(12, 0, 0) then "Manhã" else "Tarde", type text),
    IMC = Table.AddColumn(Turno, "imc", each if [peso_kg] = null then null else Number.Round([peso_kg] / ([altura_m] * [altura_m]), 1), type number)
in
    IMC
```

### resumo_nutricionista
```powerquery
let
    Fonte = consultas_nutricionista,
    Realizadas = Table.SelectRows(Fonte, each [status] = "Realizada"),
    Agrupado = Table.Group(Realizadas, {"nutricionista"}, {
        {"consultas", each Table.RowCount(_), Int64.Type},
        {"faturamento", each List.Sum([valor]), type number},
        {"duracao_media_min", each List.Average([duracao_min]), type number},
        {"minutos_atendidos", each List.Sum([duracao_min]), type number}})
in
    Agrupado
```

### contagem_por_status
```powerquery
let
    Fonte = consultas_nutricionista,
    Agrupado = Table.Group(Fonte, {"status"}, {{"consultas", each Table.RowCount(_), Int64.Type}})
in
    Agrupado
```
