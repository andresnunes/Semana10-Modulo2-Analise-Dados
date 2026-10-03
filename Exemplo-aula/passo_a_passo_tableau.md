# Tableau: limpeza, transformação, agregação e relacionamento

São os mesmos exercícios do [passo a passo do Power BI](passo_a_passo_power_bi.md), feitos agora no **Tableau Desktop** ou no **Tableau Public**, que é gratuito.

| Arquivo | Conteúdo | Objetivo principal |
|---|---|---|
| `vendas.csv` | Vendas com dados do cliente e do produto | **Primeiro nome** e **sobrenome**, **total de vendas** |
| `consultas_nutricionista.csv` | Agenda de consultas de nutricionistas | **Horário de início** e **horário de fim**, **contagem de consultas** |
| `Relacionamento/produtos.csv` | Cadastro de produtos (10 linhas) | Tabela **dimensão** (lado "1") |
| `Relacionamento/pedidos.csv` | Pedidos, apenas com o `id_produto` (30 linhas) | Tabela **fato** (lado "muitos") |

Todos os arquivos usam **`;`** como separador, **vírgula** como separador decimal, datas no formato **dd/mm/aaaa** e **UTF-8**.

> 💡 **Diferença importante em relação ao Power BI:** o Tableau Desktop **não tem um editor de limpeza** como o Power Query (a ferramenta de limpeza da Tableau é o *Tableau Prep*). No Desktop, a limpeza e as transformações são feitas com **campos calculados** e alguns atalhos da tela de *Fonte de dados*. Os nomes dos menus estão em português; entre parênteses aparece o nome em inglês, para quem usa o Tableau nesse idioma.

### Fluxo geral da aula

```
 Conectar ──► Fonte de dados ──► Campos calculados ──► Planilhas ──► Painel
 (Arquivo      (separador,        (limpar, dividir,     (agregar,     (juntar os
  de texto)     localidade,        calcular)             contar)       gráficos)
                tipos, relacionamentos)
```

---

## Parte 0: Mapa das telas

Nas tabelas de cliques, as letras entre colchetes indicam a área da tela.

### Aba "Fonte de dados" (Data Source)

```
+---------------------------------------------------------------------------------+
| [J] CONEXÕES              | [K] TELA / CANVAS                                    |
|   vendas                  |                                                      |
|   Arquivos:               |        +-------------------+                         |
|    vendas.csv             |        |  vendas.csv     v |  <- seta v = menu       |
|    consultas_...csv       |        +-------------------+     (Propriedades do    |
|  (arraste um arquivo      |                                  arquivo de texto)   |
|   para a tela)            |                                                      |
|                           +------------------------------------------------------+
|  Filtros (Adicionar)      | [L] GRADE DE DADOS                                   |
|                           |  #          Abc          Abc                         |
|                           |  Id Venda | Cliente   v | Categoria v | ...          |
|                           |  (clique no ícone = trocar tipo; seta v = Renomear,  |
|                           |   Divisão personalizada, Criar campo calculado...)   |
+---------------------------+------------------------------------------------------+
```

### Planilha (Worksheet)

```
+---------------------------------------------------------------------------------+
| [A] MENU: Arquivo | Dados | Planilha | Painel | História | Análise | Mapa | ...   |
| [B] BARRA DE FERRAMENTAS  (desfazer, salvar, trocar linhas/colunas, ordenar...) |
+-------------------+-----------+--------------------------------------+----------+
| [C] DADOS         | [D]       | [E] Colunas: [                     ] | [G]      |
|  (fonte ativa)    | Páginas   |     Linhas:  [                     ] | MOSTRE-  |
|  v vendas.csv     |-----------|--------------------------------------| ME       |
|   Abc Cliente     | Filtros   |                                      | (Show Me)|
|   Abc Categoria   |           |     [F] ÁREA DA VISUALIZAÇÃO         | tipos de |
|   ...             |-----------|     (solte os campos aqui)           | gráfico  |
|   # Quantidade    | [H]       |                                      |          |
|   # Preco Unit.   | MARCAS    |                                      |          |
|  (azul = dimensão,| Cor  Tam. |                                      |          |
|   verde = medida) | Texto Det.|                                      |          |
|                   | Dica      |                                      |          |
+-------------------+-----------+--------------------------------------+----------+
| [I] ABAS:  Fonte de dados | Planilha 1 |  [ícones: nova planilha, novo painel]  |
+---------------------------------------------------------------------------------+
```

- **Campos azuis** são *discretos* (geralmente dimensões: texto, categorias). **Campos verdes** são *contínuos* (geralmente medidas: números que o Tableau agrega com SOMA).
- Um campo arrastado para **Linhas**, **Colunas** ou **Marcas** vira uma "pílula". A seta **v** da pílula troca a agregação (Soma, Média, Contagem…).

---

## Parte 1: Conectar aos arquivos

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | Tela inicial › painel **Conectar** | **Para um arquivo** › **Arquivo de texto** (Text file) | Abre o explorador |
| 2 | Explorador | Selecione `PBI\vendas.csv` › **Abrir** | Vai para a aba **Fonte de dados** |
| 3 | [K] | Seta **v** da tabela `vendas.csv` › **Propriedades do arquivo de texto...** (Text File Properties) | Abre as configurações de leitura |
| 4 | Diálogo | Separador de campo = **Ponto e vírgula** · Conjunto de caracteres = **UTF-8** · Localidade = **Português (Brasil)** › **OK** | Números com vírgula e datas dd/mm são lidos corretamente |
| 5 | [L] | Confira a grade: `Florianópolis` com acento, `3899,9` como número | |
| 6 | [I] | Clique em **Planilha 1** | Abre a planilha |
| 7 | [A] | **Dados** › **Nova fonte de dados** › **Arquivo de texto** › `consultas_nutricionista.csv` | Repita os passos 3 e 4 |

> 💡 O Tableau **renomeia as colunas sozinho**: `id_venda` vira **Id Venda**, `preco_unitario` vira **Preco Unitario** e `uf` vira **Uf**. Este guia usa esses nomes.
>
> ⚠️ Se a *Localidade* ficar errada, `3899,90` vira texto (ícone **Abc**) ou `389990`. Volte ao passo 3.

---

## Parte 2: Vendas

Em [C], deixe ativa a fonte de dados **vendas**.

### Como criar um campo calculado (vale para o guia inteiro)

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **Análise** › **Criar campo calculado...** (ou, em [C], a seta **v** ao lado da busca › *Criar campo calculado*) | Abre o editor de cálculo |
| 2 | Editor | Digite o **nome** no campo de cima e a **fórmula** embaixo | Enquanto você digita, o editor sugere funções e campos |
| 3 | Editor (rodapé) | Confira a mensagem **"O cálculo é válido"** › **OK** | O campo aparece em [C] com um **=** antes do ícone |

### 2.1 Limpar os textos

Crie os campos calculados:

| Nome | Fórmula | O que faz |
|---|---|---|
| `Cliente Limpo` | `PROPER(TRIM([Cliente]))` | Tira os espaços e coloca a inicial de cada palavra em maiúscula |
| `Categoria Limpa` | `PROPER(TRIM([Categoria]))` | `MÓVEIS` e `informática` passam a `Móveis` e `Informática` |
| `UF Limpa` | `UPPER(TRIM([Uf]))` | `sc` passa a `SC` |

> 🔎 **Demonstração:** arraste `Categoria` (original) para **Linhas** e veja 9 valores. Troque por `Categoria Limpa` e ficam 3.

**Alternativa só com cliques: Grupo.** Serve para juntar grafias diferentes do mesmo valor.

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [C] | **Botão direito** em `Categoria` › **Criar** › **Grupo...** | Lista todos os valores |
| 2 | Diálogo | Selecione `Móveis` e `MÓVEIS` (**Ctrl** + clique) › **Agrupar** › renomeie para `Móveis` | |
| 3 | Diálogo | Repita para `Informática`/`informática` e `Eletrônicos`/`ELETRÔNICOS` › **OK** | Surge o campo `Categoria (grupo)` |

> ⚠️ Se a sua versão do Tableau não tiver a função `PROPER`, use o **Grupo** para a categoria e o campo `UPPER(TRIM([Cliente]))` para o cliente.

### 2.2 Tipos de dados

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [I] › Fonte de dados › [L] | Clique no **ícone** acima de `Data Venda` › **Data** | Ícone de calendário |
| 2 | [L] | Ícone de `Quantidade` › **Número (inteiro)** | |
| 3 | [L] | Ícone de `Preco Unitario` e de `Desconto Pct` › **Número (decimal)** | |
| 4 | Volte à planilha › [C] | **Botão direito** em `Id Venda` › **Converter em dimensão** | O campo sai das medidas: um ID não deve ser somado |

### 2.3 Duplicatas e valores vazios

**Valores vazios:** crie o campo `Desconto` com a fórmula `ZN([Desconto Pct])`. A função `ZN` troca vazio (nulo) por 0.

**Duplicatas:** o Tableau Desktop **não tem "Remover duplicatas"**. Há 5 vendas repetidas (a `1010`, por exemplo), e cada uma entra 2 vezes nas somas.

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | Planilha nova ([I] › ícone de nova planilha) | Em [C], arraste o campo **vendas.csv (Contagem)** (no fim da lista) para [H] **Texto** | Mostra **305** linhas |
| 2 | [C] | Arraste `Id Venda` com o **botão direito** do mouse para [H] **Texto** | Abre o diálogo *Soltar campo* |
| 3 | Diálogo | Escolha **CONTD(Id Venda)** (contagem distinta) › **OK** | Mostra **300** |

Por isso, neste guia:
- as **contagens** usam `COUNTD([Id Venda])`;
- as **somas** usam uma expressão LOD (explicada em 2.8), que considera **uma linha por venda**.

### 2.4 ⭐ Primeiro nome e sobrenome

**Com campos calculados (recomendado)**

| Nome | Fórmula |
|---|---|
| `Primeiro Nome` | `SPLIT([Cliente Limpo], " ", 1)` |
| `Sobrenome` | `SPLIT([Cliente Limpo], " ", -1)` |

`SPLIT(texto, separador, posição)` corta o texto no separador. A posição **1** pega o primeiro pedaço e a posição **-1** pega o **último**, contando da direita.

| Cliente Limpo | Primeiro Nome | Sobrenome |
|---|---|---|
| Ana Paula Ribeiro | Ana | Ribeiro |
| Beatriz Santos | Beatriz | Santos |
| Marcos Vinícius Teixeira | Marcos | Teixeira |

**Só com cliques: Divisão personalizada** (Custom Split)

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [C] | **Botão direito** em `Cliente` › **Transformar** › **Divisão personalizada...** | Abre o diálogo |
| 2 | Diálogo | Usar o separador = ` ` (**espaço**) · Dividir = **Primeiras** `1` colunas › **OK** | Surge `Cliente - Divisão 1` (primeiro nome) |
| 3 | [C] | Repita com Dividir = **Últimas** `1` colunas | Surge o sobrenome |
| 4 | [C] | **Botão direito** no campo novo › **Renomear** › `Primeiro Nome (divisão)` e `Sobrenome (divisão)` | |

> ⚠️ A divisão sobre o campo **original** herda os problemas dele: `carlos` continua minúsculo, e o espaço no começo de `  carlos eduardo lima` pode gerar um primeiro pedaço vazio. Por isso preferimos o `SPLIT` sobre o `Cliente Limpo`.

### 2.5 Juntar colunas

| Nome | Fórmula |
|---|---|
| `Cidade UF` | `[Cidade] + " - " + [UF Limpa]` |

**Só com cliques:** em [C], selecione `Cidade` e `Uf` (**Ctrl**), clique com o **botão direito** › **Criar** › **Campo combinado**.

### 2.6 Colunas calculadas

| Nome | Fórmula |
|---|---|
| `Valor Bruto` | `[Quantidade] * [Preco Unitario]` |
| `Valor Liquido` | `[Valor Bruto] * (1 - [Desconto] / 100)` |

**Mês:** não precisa criar uma coluna. Arraste `Data Venda` para **Colunas**, clique na seta **v** da pílula e escolha **Mês** (Maio de 2015 = mês + ano; Maio = só o mês).

### 2.7 ⭐ Agregação por categoria

No Tableau não existe "Agrupar Por": **a própria visualização agrupa**. O que estiver em Linhas ou Colunas é o agrupamento, e as medidas são agregadas automaticamente.

Antes, crie as medidas sem duplicata (a explicação está em 2.8):

| Nome | Fórmula |
|---|---|
| `Total de Vendas` | `SUM({INCLUDE [Id Venda] : MIN([Valor Liquido])})` |
| `Qtd de Vendas` | `COUNTD([Id Venda])` |
| `Itens Vendidos` | `SUM({INCLUDE [Id Venda] : MIN([Quantidade])})` |
| `Ticket Médio` | `[Total de Vendas] / [Qtd de Vendas]` |

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [I] | Nova planilha › dê **duplo clique** na aba e renomeie para `Vendas por Categoria` | |
| 2 | [C] | Arraste `Categoria Limpa` para **Linhas** | 3 linhas: Eletrônicos, Informática, Móveis |
| 3 | [C] | **Duplo clique** em `Total de Vendas` | O Tableau cria uma **tabela de texto** |
| 4 | [C] | Arraste `Qtd de Vendas`, `Itens Vendidos` e `Ticket Médio` **para dentro da tabela** | Surgem as pílulas *Nomes de medidas* / *Valores de medidas* |
| 5 | [A] | **Análise** › **Totais** › **Mostrar totais gerais de coluna** | Linha de **Total geral** |
| 6 | [G] Mostre-me | **Barras horizontais** | Vira um gráfico de barras |

**Resultado esperado:**

| Categoria Limpa | Qtd de Vendas | Total de Vendas |
|---|---|---|
| Eletrônicos | 88 | 166.540,71 |
| Informática | 114 | 183.316,02 |
| Móveis | 98 | 121.527,90 |
| **Total geral** | **300** | **471.384,63** |

> 🔎 **Demonstração da duplicata:** arraste também o campo `Valor Liquido` comum (**SOMA**). A linha **Móveis mostra 124.983,90** em vez de 121.527,90, porque as vendas 1010 e 1129 foram contadas 2 vezes. Eletrônicos também muda (172.347,96 em vez de 166.540,71).
>
> 💡 **Trocar a agregação:** na pílula `SOMA(Valor Liquido)`, clique na seta **v** › **Medida (Soma)** › **Média**, **Mínimo**, **Contagem**…

**Exercício:** troque `Categoria Limpa` por `Primeiro Nome` + `Sobrenome` em **Linhas** e ordene pelo botão **Classificar em ordem decrescente** em [B]. Quem mais comprou?

### 2.8 ⭐ Total de vendas

O valor esperado é **R$ 471.384,63** (300 vendas, 602 itens).

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [I] | Nova planilha › renomeie para `KPI Total` | |
| 2 | [C] | Arraste `Total de Vendas` para [H] **Texto** | Um número grande no centro |
| 3 | [C] | **Botão direito** em `Total de Vendas` › **Propriedades padrão** › **Formato de número...** › **Moeda (personalizada)** › Prefixo `R$ ` · 2 casas decimais › **OK** | `R$ 471.384,63` |
| 4 | [H] | Clique em **Texto** › **...** (reticências) › aumente a fonte | Fica com cara de "cartão" |
| 5 | [C] | Arraste `Categoria Limpa` para **Filtros** › **Todos** › **OK** › na pílula do filtro: seta **v** › **Mostrar filtro** | O filtro aparece à direita |
| 6 | Filtro | Deixe só **Móveis** marcado | O total muda para **R$ 121.527,90** |

**O que é `{INCLUDE [Id Venda] : MIN([Valor Liquido])}`?**
Essa é uma expressão de **nível de detalhe** (LOD). Ela funciona assim:
1. primeiro calcula `MIN(Valor Liquido)` **para cada Id Venda**, e a venda 1010, que aparece 2 vezes, gera **um único** valor;
2. depois, o `SUM` de fora soma esses valores.

Assim a duplicata não entra duas vezes.

> 💬 **Comparação para a turma:**
> - Power BI: remove a duplicata **antes**, no Power Query, e a medida é um simples `SUM`.
> - Tableau Desktop: trata a duplicata **dentro do cálculo**.
>
> Os dois caminhos chegam ao mesmo valor. Limpar antes (no Tableau Prep, por exemplo) deixa os cálculos mais simples.

---

## Parte 3: Consultas de nutricionista

Em [C], troque a fonte de dados ativa para **consultas_nutricionista**.

### 3.1 Limpar os textos

| Nome | Fórmula |
|---|---|
| `Paciente Limpo` | `PROPER(TRIM([Paciente]))` |
| `Tipo Consulta Limpo` | `PROPER(TRIM([Tipo Consulta]))` |

Converta `Id Consulta` em dimensão: em [C], **botão direito** › **Converter em dimensão**.

### 3.2 Padronizar o horário

| Nome | Fórmula | Resultado |
|---|---|---|
| `Horario Padrao` | `REPLACE([Horario], "h", ":")` | `14h00 - 14h50` passa a `14:00 - 14:50` |

> 💬 Diferente do Power BI, aqui não existe o risco de trocar o `h` de "Martins": a fórmula só olha para o campo `[Horario]`.

### 3.3 ⭐ Horário de início e horário de fim

**Passo 1: separar o texto**

| Nome | Fórmula | Exemplo |
|---|---|---|
| `Inicio Texto` | `TRIM(SPLIT([Horario Padrao], "-", 1))` | `08:00` |
| `Fim Texto` | `TRIM(SPLIT([Horario Padrao], "-", 2))` | `08:50` |

**Passo 2: transformar em horário de verdade**

O Tableau **não tem um tipo "só hora"**. Por isso, juntamos a data da consulta com a hora e obtemos um **data e hora**:

| Nome | Fórmula |
|---|---|
| `Horario Inicio` | `MAKEDATETIME([Data Consulta], MAKETIME(INT(SPLIT([Inicio Texto], ":", 1)), INT(SPLIT([Inicio Texto], ":", 2)), 0))` |
| `Horario Fim` | `MAKEDATETIME([Data Consulta], MAKETIME(INT(SPLIT([Fim Texto], ":", 1)), INT(SPLIT([Fim Texto], ":", 2)), 0))` |

Para exibir só a hora: em [C], **botão direito** em `Horario Inicio` › **Propriedades padrão** › **Formato de data...** › **Personalizado** › `hh:nn`. No Tableau, os minutos são `nn`, porque `mm` é o mês.

| Horario (original) | Horario Inicio | Horario Fim |
|---|---|---|
| `08:00 - 08:50` | 08:00 | 08:50 |
| `9:00-9:50` | 09:00 | 09:50 |
| `14h00 - 14h50` | 14:00 | 14:50 |

**Só com cliques (para comparar):** em [C], **botão direito** em `Horario` › **Transformar** › **Divisão personalizada** › separador `-` › **Todas** as colunas. Funciona, mas as linhas `14h00` continuam com `h`, então o resultado não vira hora. Por isso usamos as fórmulas acima.

### 3.4 Tipos

Na aba **Fonte de dados** › [L], confira: `Data Consulta` = **Data**, e `Peso Kg`, `Altura M` e `Valor` = **Número (decimal)**. Consultas com status *Faltou* ou *Cancelada* ficam com **Nulo** no peso e na altura, e isso está correto.

### 3.5 Campos derivados do horário

| Nome | Fórmula |
|---|---|
| `Duracao Min` | `DATEDIFF('minute', [Horario Inicio], [Horario Fim])` |
| `Turno` | `IF DATEPART('hour', [Horario Inicio]) < 12 THEN "Manhã" ELSE "Tarde" END` |
| `IMC` | `ROUND([Peso Kg] / ([Altura M] * [Altura M]), 1)` |

### 3.6 ⭐ Agregação por nutricionista

Medidas sem duplicata (há 4 consultas repetidas):

| Nome | Fórmula |
|---|---|
| `Faturamento Consultas` | `SUM({INCLUDE [Id Consulta] : MIN([Valor])})` |
| `Duracao Media` | `AVG({INCLUDE [Id Consulta] : MIN([Duracao Min])})` |
| `Minutos Atendidos` | `SUM({INCLUDE [Id Consulta] : MIN([Duracao Min])})` |

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [I] | Nova planilha `Resumo Nutricionista` | |
| 2 | [C] | Arraste `Status` para **Filtros** › marque só **Realizada** › **OK** | |
| 3 | [C] | Arraste `Nutricionista` para **Linhas** | 3 linhas |
| 4 | [C] | **Duplo clique** em `Total de Consultas` (criado em 3.7), `Faturamento Consultas` e `Duracao Media` | Tabela de texto com 3 medidas |

Resultado esperado: André **62**, Camila **58** e Luiza **58** consultas. Duração média: Camila **36,7**, Luiza **33,4**, André **33,5** minutos.

**Exercício:** arraste `Tipo Consulta Limpo` para **Colunas**.

### 3.7 ⭐ Contagem de consultas

Valores esperados: **221 consultas no total**, sendo **178 Realizadas**, **31 Faltou** e **12 Cancelada**.

| Nome | Fórmula |
|---|---|
| `Total de Consultas` | `COUNTD([Id Consulta])` |
| `Consultas Realizadas` | `COUNTD(IF [Status] = "Realizada" THEN [Id Consulta] END)` |
| `Ausências` | `COUNTD(IF [Status] <> "Realizada" THEN [Id Consulta] END)` |
| `Taxa de Ausência` | `[Ausências] / [Total de Consultas]` |
| `Pacientes Atendidos` | `COUNTD(IF [Status] = "Realizada" THEN [Paciente Limpo] END)` |

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [I] | Nova planilha `KPI Consultas` | |
| 2 | [C] | **Antes de converter em dimensão**, arraste `Id Consulta` para [H] **Texto** | ⚠️ Mostra **24.894**: o Tableau **somou** os IDs (e as consultas repetidas duas vezes!) |
| 3 | [H] | Seta **v** da pílula › **Medida** › **Contagem (distinta)** | Agora mostra **221** ✅ |
| 4 | [C] | Arraste `Consultas Realizadas`, `Ausências` e `Taxa de Ausência` | 178 / 43 / 0,195 |
| 5 | [C] | **Botão direito** em `Taxa de Ausência` › **Propriedades padrão** › **Formato de número** › **Porcentagem** | **19,5%** |

**Gráfico por status**

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [I] | Nova planilha | |
| 2 | [C] | `Status` para **Colunas**, `Total de Consultas` para **Linhas** | Barras: Realizada 178, Faltou 31, Cancelada 12 |
| 3 | [C] | `Nutricionista` para [H] **Cor** | As barras ficam empilhadas por nutricionista |
| 4 | [H] | Arraste `Total de Consultas` também para **Rótulo** | Os números aparecem nas barras |

`Pacientes Atendidos` = **32**. Por tipo (realizadas): Retorno **137**, Primeira Consulta **21**, Avaliação Esportiva **20**.

> 💬 **Ponto para a turma:** o Tableau também soma os números por padrão, até IDs. Converter o campo em **dimensão** evita o erro. A diferença entre **CONT** e **CONTD** mostra o efeito da linha duplicada: 225 × 221.

---

## Parte 4: Painel (Dashboard)

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **Painel** › **Novo painel** | Abre a tela do painel; as planilhas ficam listadas à esquerda |
| 2 | Painel › esquerda | Arraste `KPI Total`, `Vendas por Categoria`, `KPI Consultas` e o gráfico por status | |
| 3 | Planilha `Vendas por Categoria` no painel | Clique nela › ícone de **funil** (*Usar como filtro*) | Clicar numa categoria filtra as outras planilhas **da mesma fonte** |
| 4 | Filtro de categoria | Seta **v** › **Aplicar a planilhas** › **Todas usando esta fonte de dados** | O filtro vale para todas as planilhas de vendas |

> 📁 O **Tableau Public** salva só na nuvem (Arquivo › Salvar no Tableau Public). O **Tableau Desktop** salva `.twb`/`.twbx`.

---

## Parte 5: ⭐ Relacionamento entre tabelas

```
        produtos  (dimensão)                        pedidos  (fato)
  +---------------------------+              +---------------------------+
  | Id Produto  (chave)   [1] |------------<*| Id Produto                |
  | Produto                   |   1 : muitos | Id Pedido                 |
  | Categoria                 |              | Data Pedido               |
  | Marca                     |              | Quantidade                |
  | Preco Unitario            |              | Vendedor                  |
  +---------------------------+              +---------------------------+
```

Há duas "armadilhas" nos dados, colocadas de propósito:
- o produto **P10** (Luminária) **nunca foi vendido**;
- o pedido **14** usa o **P11**, que **não existe** no cadastro.

> 📁 Use uma **pasta de trabalho nova** (Arquivo › Novo).

### 5.1 Conectar e relacionar (a "linha" do Tableau)

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | Conectar | **Arquivo de texto** › `Relacionamento\produtos.csv` | `produtos.csv` aparece em [K] |
| 2 | [K] | Seta **v** › **Propriedades do arquivo de texto** › `;` · UTF-8 · Português (Brasil) › **OK** | |
| 3 | [J] Arquivos | **Arraste** `pedidos.csv` para a tela, **ao lado** de `produtos.csv` | Uma **linha** ("noodle") liga as duas tabelas e abre o painel do relacionamento |
| 4 | Painel do relacionamento | Confira: `Id Produto` **=** `Id Produto` | O Tableau escolhe sozinho, porque os nomes são iguais |
| 5 | Painel › **Opções de desempenho** | Cardinalidade: produtos = **Um**, pedidos = **Muitos** · Integridade referencial = **Alguns registros correspondem** | Informa ao Tableau como os dados são |
| 6 | Seta **v** de `pedidos.csv` › Propriedades do arquivo de texto | `;` · UTF-8 · Português (Brasil) › **OK** | |

> 🔍 **Para inspecionar:** passe o mouse sobre a linha e **clique nela** para reabrir o painel. Para desfazer, arraste `pedidos.csv` para fora da tela.
>
> 💬 **Sem o relacionamento**, o Tableau nem deixa usar as duas tabelas na mesma fonte de dados. Se você conectar só `pedidos.csv`, não existe nenhum campo `Categoria` para escolher.

### 5.2 Ver o relacionamento funcionando

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [I] | Planilha 1 | Em [C], os campos aparecem **separados por tabela** |
| 2 | [C] | `Categoria` (de produtos) para **Linhas** | |
| 3 | [C] | **Duplo clique** em `Quantidade` (de pedidos) e em **pedidos.csv (Contagem)** | |

| Categoria | pedidos.csv (Contagem) | Quantidade |
|---|---|---|
| Eletrônicos | 11 | 19 |
| Informática | 13 | 25 |
| Móveis | 5 | 7 |
| **Nulo** | 1 | 2 |

> 🧐 **O que é "Nulo"?** É o pedido 14, com o produto **P11**, que não existe em `produtos`. O relacionamento do Tableau **não descarta** esse pedido.
>
> Troque `Categoria` por `Produto`: a **Luminária de Mesa** (P10) também aparece, com a contagem vazia. Isso também é o relacionamento: ele mantém os valores das duas tabelas, mesmo quando não há correspondência.

### 5.3 Filtro atravessando as tabelas

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | Nova planilha | `Vendedor` (de **pedidos**) para **Linhas**, `Quantidade` para [H] **Texto** | Paula, Ricardo, Sandra |
| 2 | [C] | `Categoria` (de **produtos**) para **Filtros** › só **Móveis** › **OK** | A quantidade de cada vendedor muda: um campo de `produtos` filtrou `pedidos` |

> 💬 No Tableau, o filtro sempre funciona **nos dois sentidos**, porque não existe a opção "Único/Ambas" do Power BI.

### 5.4 Faturamento: quando precisa de junção (join)

O faturamento é `Quantidade` (de pedidos) × `Preco Unitario` (de produtos), **linha a linha**. Num relacionamento, o Tableau **não permite** um cálculo linha a linha com campos de **tabelas lógicas diferentes**: o editor mostra um erro. A solução é fazer uma **junção** na camada física.

| # | Onde | Clique | O que acontece |
|---|---|---|---|
| 1 | [A] | **Dados** › **Nova fonte de dados** › **Arquivo de texto** › `pedidos.csv` | Nova fonte de dados com uma tabela só |
| 2 | [K] | **Duplo clique** em `pedidos.csv` | Abre a **camada física** ("pedidos.csv é composto de 1 tabela") |
| 3 | [J] | Arraste `produtos.csv` para **dentro** dessa área, ao lado de `pedidos.csv` | Aparece o ícone de **junção** (dois círculos) |
| 4 | Ícone de junção | Clique › escolha **Esquerda** (Left) · Cláusula `Id Produto` = `Id Produto` | |
| 5 | [K] | Feche a camada física (**X**) › renomeie a fonte para `pedidos + produtos (junção)` | |
| 6 | Planilha | **Análise** › **Criar campo calculado**: `Faturamento` = `SUM([Quantidade] * [Preco Unitario])` | Agora é válido ✅ |

**Resultado esperado** (fonte com junção):

| Categoria | Faturamento |
|---|---|
| Eletrônicos | R$ 24.190,00 |
| Informática | R$ 22.283,90 |
| Móveis | R$ 7.445,70 |
| Nulo | *(vazio)* |
| **Total** | **R$ 53.919,60** |

| Vendedor | Faturamento |
|---|---|
| Paula | R$ 12.412,50 |
| Ricardo | R$ 19.833,20 |
| Sandra | R$ 21.673,90 |

> 🧪 **Experimento:** troque a junção para **Interna** (Inner). O pedido 14 **some**: ficam 29 pedidos e 51 itens. A **Luminária** (P10) também não aparece em nenhuma das duas junções. Compare com o relacionamento da 5.2, que mantinha os dois casos.

### 5.5 Relacionamento × Junção

| | Relacionamento (camada lógica, "linha") | Junção (camada física, "Venn") |
|---|---|---|
| Como cria | Arrastar a tabela para o lado | Duplo clique na tabela e arrastar para dentro |
| Tabelas | Continuam separadas | Viram uma tabela só |
| Linhas sem correspondência | Mantidas (P10 e P11 aparecem) | Dependem do tipo: Interna, Esquerda, Direita, Externa completa |
| Cálculo linha a linha com as 2 tabelas | ❌ Não permite | ✅ Permite |
| Quando usar | **Padrão** para modelar | Quando precisa calcular linha a linha com campos das duas tabelas |

> 💬 **Comparação com o Power BI:** o relacionamento do Tableau é parecido com o do Power BI (Parte 5 do outro guia). A junção é parecida com o **Mesclar Consultas** do Power Query. No Power BI, o `RELATED` permite o cálculo linha a linha mesmo com as tabelas separadas.

---

## Apêndice: todos os campos calculados

### Fonte `vendas`
```
Cliente Limpo      = PROPER(TRIM([Cliente]))
Categoria Limpa    = PROPER(TRIM([Categoria]))
UF Limpa           = UPPER(TRIM([Uf]))
Desconto           = ZN([Desconto Pct])
Primeiro Nome      = SPLIT([Cliente Limpo], " ", 1)
Sobrenome          = SPLIT([Cliente Limpo], " ", -1)
Cidade UF          = [Cidade] + " - " + [UF Limpa]
Valor Bruto        = [Quantidade] * [Preco Unitario]
Valor Liquido      = [Valor Bruto] * (1 - [Desconto] / 100)
Total de Vendas    = SUM({INCLUDE [Id Venda] : MIN([Valor Liquido])})
Qtd de Vendas      = COUNTD([Id Venda])
Itens Vendidos     = SUM({INCLUDE [Id Venda] : MIN([Quantidade])})
Ticket Médio       = [Total de Vendas] / [Qtd de Vendas]
```

### Fonte `consultas_nutricionista`
```
Paciente Limpo        = PROPER(TRIM([Paciente]))
Tipo Consulta Limpo   = PROPER(TRIM([Tipo Consulta]))
Horario Padrao        = REPLACE([Horario], "h", ":")
Inicio Texto          = TRIM(SPLIT([Horario Padrao], "-", 1))
Fim Texto             = TRIM(SPLIT([Horario Padrao], "-", 2))
Horario Inicio        = MAKEDATETIME([Data Consulta], MAKETIME(INT(SPLIT([Inicio Texto], ":", 1)), INT(SPLIT([Inicio Texto], ":", 2)), 0))
Horario Fim           = MAKEDATETIME([Data Consulta], MAKETIME(INT(SPLIT([Fim Texto], ":", 1)), INT(SPLIT([Fim Texto], ":", 2)), 0))
Duracao Min           = DATEDIFF('minute', [Horario Inicio], [Horario Fim])
Turno                 = IF DATEPART('hour', [Horario Inicio]) < 12 THEN "Manhã" ELSE "Tarde" END
IMC                   = ROUND([Peso Kg] / ([Altura M] * [Altura M]), 1)
Total de Consultas    = COUNTD([Id Consulta])
Consultas Realizadas  = COUNTD(IF [Status] = "Realizada" THEN [Id Consulta] END)
Ausências             = COUNTD(IF [Status] <> "Realizada" THEN [Id Consulta] END)
Taxa de Ausência      = [Ausências] / [Total de Consultas]
Pacientes Atendidos   = COUNTD(IF [Status] = "Realizada" THEN [Paciente Limpo] END)
Faturamento Consultas = SUM({INCLUDE [Id Consulta] : MIN([Valor])})
Duracao Media         = AVG({INCLUDE [Id Consulta] : MIN([Duracao Min])})
Minutos Atendidos     = SUM({INCLUDE [Id Consulta] : MIN([Duracao Min])})
```

### Fonte `pedidos + produtos (junção)`
```
Faturamento = SUM([Quantidade] * [Preco Unitario])
```
