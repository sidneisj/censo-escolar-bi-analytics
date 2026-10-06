# Configuração do Tableau Cloud

## 1. Ambiente

A camada de visualização do projeto é desenvolvida utilizando o **Tableau Cloud**, por meio do ambiente de Web Authoring.

A fonte de dados utilizada é:

`data/processed/censo_escolar_tableau_2019_2025.csv`

A base foi preparada e validada previamente durante as etapas de ETL e modelagem analítica.

---

## 2. Fonte de dados

A fonte carregada no Tableau possui:

- período: 2019 a 2025;
- granularidade: Escola × Ano;
- 1.545.901 registros;
- 33 campos;
- nenhuma chave analítica duplicada;
- nenhuma chave analítica nula.

O Tableau utiliza uma única tabela analítica, sem joins ou relacionamentos adicionais.

---

## 3. Configuração dos campos

Os identificadores e códigos foram tratados como dimensões, evitando agregações inadequadas.

Exemplos:

- Código da Escola;
- Código da Região;
- Código da UF;
- Código do Município;
- ID Escola × Ano.

Os principais indicadores quantitativos foram configurados como medidas:

- Matrículas;
- Docentes;
- Salas Utilizadas;
- Escola Ativa.

O campo Ano permanece como número inteiro e dimensão, pois a periodicidade da base é exclusivamente anual.

---

## 4. Nomes de apresentação

Os nomes técnicos da fonte foram adaptados para nomes amigáveis no Tableau.

Exemplos:

| Campo de origem | Nome no Tableau |
|---|---|
| `NU_ANO_CENSO` | Ano |
| `CO_ENTIDADE` | Código da Escola |
| `NO_ENTIDADE` | Escola |
| `NO_REGIAO` | Região |
| `SG_UF` | UF |
| `NO_UF` | Estado |
| `NO_MUNICIPIO` | Município |
| `DS_REDE` | Rede |
| `DS_DEPENDENCIA` | Dependência Administrativa |
| `DS_LOCALIZACAO` | Localização |
| `DS_SITUACAO_FUNCIONAMENTO` | Situação de Funcionamento |
| `QT_MAT_BAS` | Matrículas |
| `QT_DOC_BAS` | Docentes |
| `QT_SALAS_UTILIZADAS` | Salas Utilizadas |
| `FL_ESCOLA_ATIVA` | Escola Ativa |

Os nomes físicos permanecem preservados na fonte original para garantir rastreabilidade com o processo de ETL.

---

## 5. Configuração geográfica

Durante os testes de geocodificação foi identificado que o Tableau poderia interpretar siglas brasileiras de UF sem contexto geográfico como localidades dos Estados Unidos.

Para eliminar essa ambiguidade foi criado no Tableau o campo calculado:

`País`

com a expressão:

```text
"Brasil"
```

O campo foi configurado com o papel geográfico:

`País/Região`

A configuração geográfica adotada ficou:

| Campo | Papel geográfico |
|---|---|
| País | País/Região |
| Estado | Estado/Província |
| Município | Condado / County |
| UF | Nenhum papel geográfico |
| Região | Nenhum papel geográfico |

O papel `Condado / County` foi utilizado para Município devido à estrutura de geocodificação disponível para municípios brasileiros no Tableau.

Após a inclusão do contexto de País e Estado, os municípios passaram a ser corretamente posicionados no mapa do Brasil.

---

## 6. Hierarquia analítica e geocodificação

A hierarquia analítica definida para os dashboards continua sendo:

`Brasil → Região → UF → Município`

Entretanto, a estrutura utilizada pelo mecanismo de geocodificação do Tableau é:

`Brasil → Estado → Município`

Essas estruturas possuem objetivos diferentes.

A primeira é utilizada para navegação e análise dos dados.

A segunda fornece contexto para o mecanismo geográfico do Tableau localizar corretamente os municípios brasileiros.

---

## 7. Fonte única

Não foram adicionadas tabelas complementares, joins ou relacionamentos dentro do Tableau.

A arquitetura permanece:

```text
Base analítica validada
        ↓
censo_escolar_tableau_2019_2025.csv
        ↓
Tableau Cloud
        ↓
Visualizações e dashboards
```

Essa abordagem mantém a implementação alinhada à estratégia de modelagem definida durante a M5.

---

## 8. Validação inicial

A fonte foi carregada com sucesso no Tableau Cloud.

Foram verificados:

- presença dos 33 campos;
- reconhecimento da série histórica;
- tipos de dados;
- dimensões e medidas;
- nomes de apresentação;
- papéis geográficos;
- localização dos municípios brasileiros no mapa.

Com isso, a fonte está preparada para criação das hierarquias, campos calculados e visualizações.

---

## 9. Hierarquias e campos calculados

Após a configuração inicial da fonte de dados, foram implementadas no Tableau Cloud as hierarquias e medidas calculadas definidas durante a etapa de modelagem analítica.

### 9.1 Hierarquia Geografia

Foi criada a hierarquia:

`Região → UF → Município`

A estrutura foi validada no Tableau por meio de drill-down entre os três níveis.

O contexto técnico utilizado para geocodificação permanece separado da hierarquia analítica:

`País → Estado → Município`

Dessa forma, País e Estado auxiliam o mecanismo de mapas, enquanto Região, UF e Município representam a navegação analítica utilizada nos dashboards.

### 9.2 Hierarquia Estrutura Administrativa

Foi criada a hierarquia:

`Rede → Dependência Administrativa`

O drill-down foi validado com a seguinte estrutura:

```text
Pública
├── Federal
├── Estadual
└── Municipal

Privada
└── Privada
```

### 9.3 Indicadores de infraestrutura

Foram criados campos calculados para os indicadores de infraestrutura considerando somente escolas em atividade.

O padrão utilizado foi:

```text
IF [Escola Ativa] = 1 THEN
    [Indicador]
END
```

Foram implementados campos para:

- Internet;
- Biblioteca;
- Sala de Leitura;
- Laboratório de Ciências;
- Laboratório de Informática;
- Quadra de Esportes;
- Banheiro PNE;
- Água Potável;
- Esgoto em Rede Pública;
- Energia em Rede Pública.

Os percentuais são calculados utilizando a média dos indicadores binários:

`AVG([Indicador - Escola Ativa])`

Essa abordagem preserva:

- `1` como presença do recurso;
- `0` como ausência do recurso;
- `NULL` fora do denominador.

### 9.4 Acessibilidade

Como o campo original `IN_ACESSIBILIDADE_INEXISTENTE` possui interpretação inversa, foi criado o campo positivo:

`Acessibilidade - Escola Ativa`

utilizando a lógica:

```text
IF [Escola Ativa] = 1 THEN
    IF ISNULL([Acessibilidade Inexistente]) THEN
        NULL
    ELSE
        1 - [Acessibilidade Inexistente]
    END
END
```

O resultado passa a ser interpretado como:

- `1` = possui algum recurso de acessibilidade;
- `0` = não possui recurso de acessibilidade;
- `NULL` = informação não disponível.

### 9.5 Medidas de contagem

Também foram criados os campos calculados:

**Escolas Distintas**

`COUNTD([Código da Escola])`

**Registros Escola × Ano**

`COUNTD([ID Escola × Ano])`

**Escolas Ativas Distintas**

```text
COUNTD(
    IF [Escola Ativa] = 1 THEN
        [Código da Escola]
    END
)
```

Essas medidas permitem diferenciar escolas únicas de observações históricas Escola × Ano.

### 9.6 Validação no Tableau Cloud

Os cálculos foram testados diretamente no Tableau Cloud utilizando o ano de 2025.

Foram confirmados os KPIs:

- Matrículas: `46.018.380`;
- Docentes: `2.992.045`;
- Escolas Ativas: `180.540`;
- Salas Utilizadas: `1.646.884`.

Também foram confirmadas as contagens:

- Escolas Distintas: `214.192`;
- Registros Escola × Ano: `214.192`;
- Escolas Ativas Distintas: `180.540`.

Indicadores de infraestrutura testados:

- Internet: `94,58%`;
- Acessibilidade: `78,51%`.

As hierarquias Geografia e Estrutura Administrativa também foram validadas por meio de drill-down.

Com isso, as hierarquias e os principais campos calculados estão prontos para utilização nos dashboards.

---

## 10. Estrutura visual e wireframes dos dashboards

Antes da construção definitiva das visualizações foi definida a arquitetura visual dos dashboards do projeto.

O objetivo é manter uma experiência consistente entre as diferentes análises e evitar a criação de gráficos sem função analítica clara.

---

## 10.1 Estrutura geral

O projeto será composto por quatro dashboards principais:

1. **Panorama Geral**
2. **Evolução Histórica**
3. **Geografia e Estrutura Administrativa**
4. **Infraestrutura Escolar**

Cada dashboard possuirá um objetivo analítico específico, evitando repetição excessiva de informações.

---

## 10.2 Dimensão dos dashboards

A primeira versão será desenvolvida para visualização em desktop.

Tamanho de referência:

`1200 × 800 px`

Os quatro dashboards deverão utilizar o mesmo tamanho para manter consistência visual.

Adaptações para outros dispositivos poderão ser avaliadas após a conclusão da versão principal.

---

## 10.3 Estrutura visual comum

Todos os dashboards deverão seguir a mesma estrutura básica:

```text
┌────────────────────────────────────────────────────────────┐
│ TÍTULO DO PROJETO                     Navegação            │
│ Censo Escolar — Panorama da Educação Brasileira            │
├────────────────────────────────────────────────────────────┤
│ Filtros                                                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│                    ÁREA ANALÍTICA                           │
│                                                            │
├────────────────────────────────────────────────────────────┤
│ Fonte: INEP — Censo Escolar | Período: 2019–2025           │
└────────────────────────────────────────────────────────────┘
```

A navegação prevista será:

`Panorama | Evolução | Geografia | Infraestrutura`

A implementação das ações de navegação será realizada posteriormente.

---

# 10.4 Dashboard 1 — Panorama Geral

## Objetivo

Apresentar uma visão executiva do cenário da educação básica brasileira no ano selecionado.

Esse será o dashboard inicial do projeto.

## Título

**Panorama Geral da Educação Básica**

## KPIs principais

Quatro indicadores serão apresentados em destaque:

- Matrículas;
- Docentes;
- Escolas Ativas;
- Salas Utilizadas.

O contexto padrão será um único ano.

Para 2025, os valores de referência são:

- Matrículas: `46.018.380`;
- Docentes: `2.992.045`;
- Escolas Ativas: `180.540`;
- Salas Utilizadas: `1.646.884`.

## Visualizações

Além dos quatro KPIs, serão utilizadas:

### Matrículas por Região

Tipo:

`Bar chart`

Objetivo:

comparar o volume de matrículas entre as cinco regiões brasileiras.

---

### Matrículas por Rede

Tipo:

`Bar chart / percentual`

Categorias:

- Pública;
- Privada.

Objetivo:

mostrar a distribuição das matrículas entre as redes.

---

### Escolas Ativas por Dependência Administrativa

Tipo:

`Bar chart`

Categorias:

- Federal;
- Estadual;
- Municipal;
- Privada.

---

### Escolas Ativas por Localização

Tipo:

`Bar chart`

Categorias:

- Urbana;
- Rural.

---

## Filtros

Filtros previstos:

- Ano;
- Região;
- UF;
- Rede.

O filtro Ano deverá permanecer claramente visível.

---

## Wireframe

```text
┌──────────────────────────────────────────────────────────────┐
│ PANORAMA GERAL                    Panorama | Evolução | ...  │
├──────────────────────────────────────────────────────────────┤
│ Ano       Região       UF       Rede                         │
├──────────────────────────────────────────────────────────────┤
│ Matrículas │ Docentes │ Escolas Ativas │ Salas Utilizadas   │
│   KPI      │   KPI    │      KPI       │       KPI          │
├──────────────────────────────┬───────────────────────────────┤
│ Matrículas por Região        │ Matrículas por Rede           │
│                              │                               │
│ BAR CHART                    │ BAR CHART                     │
├──────────────────────────────┼───────────────────────────────┤
│ Escolas por Dependência      │ Urbana × Rural                │
│                              │                               │
│ BAR CHART                    │ BAR CHART                     │
├──────────────────────────────┴───────────────────────────────┤
│ Fonte: INEP — Censo Escolar | 2019–2025                     │
└──────────────────────────────────────────────────────────────┘
```

---

# 10.5 Dashboard 2 — Evolução Histórica

## Objetivo

Apresentar a evolução dos principais indicadores do Censo Escolar entre 2019 e 2025.

## Título

**Evolução da Educação Básica — 2019 a 2025**

## Indicadores

Serão analisados:

- Matrículas;
- Docentes;
- Escolas Ativas;
- Salas Utilizadas.

## Visualizações

Cada indicador terá sua própria série temporal.

Isso evita colocar medidas de escalas muito diferentes no mesmo eixo.

### Evolução de Matrículas

Tipo:

`Line chart`

### Evolução de Docentes

Tipo:

`Line chart`

### Evolução de Escolas Ativas

Tipo:

`Line chart`

### Evolução de Salas Utilizadas

Tipo:

`Line chart`

Também poderão ser exibidas:

- variação absoluta em relação ao ano anterior;
- variação percentual em relação ao ano anterior.

As referências deverão ser comparadas com:

`documentation/exploracao/evolucao_kpis_2019_2025.csv`

## Filtros

- Região;
- UF;
- Rede;
- Dependência Administrativa;
- Localização.

O filtro de Ano não será utilizado como filtro de um único período nessa tela, pois o objetivo é justamente preservar a série temporal.

---

## Wireframe

```text
┌──────────────────────────────────────────────────────────────┐
│ EVOLUÇÃO HISTÓRICA               Panorama | Evolução | ...  │
├──────────────────────────────────────────────────────────────┤
│ Região      UF      Rede      Dependência      Localização   │
├──────────────────────────────┬───────────────────────────────┤
│ Matrículas                   │ Docentes                       │
│                              │                               │
│ LINE CHART                   │ LINE CHART                    │
│ 2019 ─────────────── 2025    │ 2019 ─────────────── 2025     │
├──────────────────────────────┼───────────────────────────────┤
│ Escolas Ativas               │ Salas Utilizadas              │
│                              │                               │
│ LINE CHART                   │ LINE CHART                    │
│ 2019 ─────────────── 2025    │ 2019 ─────────────── 2025     │
├──────────────────────────────┴───────────────────────────────┤
│ Fonte: INEP — Censo Escolar | 2019–2025                     │
└──────────────────────────────────────────────────────────────┘
```

---

# 10.6 Dashboard 3 — Geografia e Estrutura Administrativa

## Objetivo

Permitir exploração territorial dos indicadores educacionais e comparação entre redes e dependências administrativas.

## Título

**Distribuição Geográfica e Administrativa**

## Visualizações

### Mapa do Brasil

O mapa será a principal visualização do dashboard.

Para evitar excesso de marcas e problemas de desempenho, a visão nacional não deverá iniciar exibindo individualmente todas as escolas ou todos os municípios.

A primeira visualização deverá priorizar agregação por:

`UF`

O detalhamento poderá posteriormente chegar ao Município por interação ou drill-down.

Contexto geográfico utilizado:

`País → Estado → Município`

Hierarquia analítica:

`Região → UF → Município`

---

### Ranking geográfico

Tipo:

`Horizontal bar chart`

Permitirá comparar:

- Regiões;
- UFs;
- eventualmente Municípios após seleção.

A métrica apresentada poderá variar conforme a análise, priorizando inicialmente Matrículas.

---

### Rede Pública × Privada

Tipo:

`Bar chart`

Categorias:

- Pública;
- Privada.

---

### Dependência Administrativa

Tipo:

`Bar chart`

Categorias:

- Federal;
- Estadual;
- Municipal;
- Privada.

---

## Filtros

- Ano;
- Rede;
- Dependência Administrativa;
- Localização.

Região, UF e Município poderão ser utilizados pela própria interação geográfica.

---

## Wireframe

```text
┌──────────────────────────────────────────────────────────────┐
│ GEOGRAFIA E ADMINISTRAÇÃO        Panorama | Evolução | ...  │
├──────────────────────────────────────────────────────────────┤
│ Ano       Rede       Dependência       Localização           │
├──────────────────────────────────────┬───────────────────────┤
│                                      │ Ranking Geográfico    │
│                                      │                       │
│           MAPA DO BRASIL             │ HORIZONTAL BAR        │
│                                      │                       │
│                                      │                       │
├──────────────────────────────────────┼───────────────────────┤
│ Rede Pública × Privada               │ Dependência           │
│                                      │ Administrativa        │
│ BAR CHART                            │ BAR CHART             │
├──────────────────────────────────────┴───────────────────────┤
│ Fonte: INEP — Censo Escolar | 2019–2025                     │
└──────────────────────────────────────────────────────────────┘
```

---

# 10.7 Dashboard 4 — Infraestrutura Escolar

## Objetivo

Comparar a disponibilidade de recursos de infraestrutura nas escolas brasileiras.

## Título

**Infraestrutura das Escolas Brasileiras**

## Indicadores

Serão analisados:

- Internet;
- Biblioteca;
- Sala de Leitura;
- Laboratório de Ciências;
- Laboratório de Informática;
- Quadra de Esportes;
- Banheiro PNE;
- Acessibilidade;
- Água Potável;
- Esgoto em Rede Pública;
- Energia em Rede Pública.

Os percentuais deverão considerar:

- somente escolas em atividade;
- somente registros com informação válida;
- `1` como presença do recurso;
- `0` como ausência;
- `NULL` excluído do denominador.

---

## Visualização principal

Será utilizado um gráfico de barras horizontais comparando os percentuais de infraestrutura.

Exemplo conceitual:

```text
Internet                    ███████████████████ 94,58%
Água Potável                ██████████████████  XX,XX%
Energia em Rede Pública     █████████████████   XX,XX%
Acessibilidade              ███████████████     78,51%
Biblioteca                  ███████████         XX,XX%
...
```

A utilização de barras facilita a comparação entre muitos indicadores melhor do que múltiplos gráficos independentes.

---

## Visualização complementar

Também será prevista uma análise comparativa por:

- Rede;
- Região;
- Localização.

A implementação poderá utilizar barras agrupadas ou outra visualização comparativa adequada.

---

## Filtros

- Ano;
- Região;
- UF;
- Rede;
- Localização.

---

## Wireframe

```text
┌──────────────────────────────────────────────────────────────┐
│ INFRAESTRUTURA ESCOLAR           Panorama | Evolução | ...  │
├──────────────────────────────────────────────────────────────┤
│ Ano       Região       UF       Rede       Localização       │
├──────────────────────────────────────┬───────────────────────┤
│                                      │ Comparação por Rede   │
│ Internet                 94,58%      │ / Região / Localização│
│ Água Potável             XX,XX%      │                       │
│ Energia                  XX,XX%      │ BAR CHART             │
│ Acessibilidade           78,51%      │                       │
│ Biblioteca               XX,XX%      │                       │
│ ...                                  │                       │
│                                      │                       │
│ HORIZONTAL BAR CHART                 │                       │
├──────────────────────────────────────┴───────────────────────┤
│ Fonte: INEP — Censo Escolar | 2019–2025                     │
└──────────────────────────────────────────────────────────────┘
```

---

# 10.8 Padrão de filtros

Nem todos os filtros serão exibidos em todos os dashboards.

A configuração inicial será:

| Dashboard | Filtros |
|---|---|
| Panorama Geral | Ano, Região, UF, Rede |
| Evolução Histórica | Região, UF, Rede, Dependência, Localização |
| Geografia | Ano, Rede, Dependência, Localização |
| Infraestrutura | Ano, Região, UF, Rede, Localização |

Filtros adicionais poderão ser incorporados somente quando trouxerem benefício analítico claro.

---

# 10.9 Padrão visual

Os dashboards deverão seguir os seguintes princípios:

- fundo predominantemente claro;
- alto contraste entre texto e fundo;
- poucos elementos decorativos;
- títulos curtos;
- KPIs com destaque visual;
- mesma identidade visual em todas as telas;
- cores utilizadas de forma consistente;
- evitar gráficos 3D;
- evitar excesso de gráficos de pizza ou donut;
- utilizar barras para comparação categórica;
- utilizar linhas para séries temporais;
- priorizar legibilidade;
- manter fonte e período dos dados visíveis.

A definição final de cores será realizada durante a construção visual, preservando consistência entre dashboards.

---

# 10.10 Nomenclatura no workbook

Os dashboards serão nomeados:

- `D01 - Panorama Geral`
- `D02 - Evolução Histórica`
- `D03 - Geografia e Administração`
- `D04 - Infraestrutura Escolar`

As worksheets deverão utilizar prefixo `WS`.

Exemplos:

- `WS01 - KPI Matrículas`
- `WS02 - KPI Docentes`
- `WS03 - KPI Escolas Ativas`
- `WS04 - KPI Salas`
- `WS05 - Matrículas por Região`

Essa convenção facilita a organização do workbook e a identificação das folhas utilizadas em cada dashboard.

---

# 10.11 Ordem de implementação

A construção seguirá a ordem das issues da M6:

1. Panorama Geral;
2. Geografia e Estrutura Administrativa;
3. Infraestrutura Escolar;
4. Evolução Histórica;
5. filtros, ações e navegação;
6. validação final.

Embora Evolução Histórica seja o segundo dashboard na navegação, sua construção ocorrerá após as demais telas conforme a organização das issues do projeto.

---

## 10.12 Resultado da etapa

Com esta definição, cada dashboard possui:

- objetivo analítico;
- conteúdo;
- KPIs;
- tipos de visualização;
- filtros;
- estrutura de layout;
- padrão de navegação;
- wireframe.

A construção das visualizações poderá, portanto, iniciar sem necessidade de redefinir a arquitetura geral do produto.

---

## 11. Dashboard Panorama Geral

Foi implementado o primeiro dashboard analítico do projeto:

`D01 - Panorama Geral`

O objetivo da tela é apresentar uma visão executiva do Censo Escolar para o ano selecionado, permitindo análises rápidas por recortes geográficos e administrativos.

### 11.1 Estrutura do dashboard

O dashboard foi desenvolvido em layout desktop com tamanho fixo:

`1200 × 800 px`

A estrutura visual é composta por:

- cabeçalho com título e subtítulo;
- faixa de filtros;
- quatro KPIs;
- quatro visualizações analíticas;
- rodapé com identificação da fonte e período analisado.

### 11.2 Filtros

Foram disponibilizados os seguintes filtros:

- Ano;
- Região;
- UF;
- Rede.

O estado padrão do dashboard é:

- Ano: `2025`;
- Região: `(Tudo)`;
- UF: `(Tudo)`;
- Rede: `(Tudo)`.

O filtro `Ano` utiliza seleção única.

Os filtros `Região`, `UF` e `Rede` permitem múltiplos valores.

O filtro `UF` utiliza somente valores relevantes, permitindo que a lista de estados seja restringida de acordo com a Região selecionada.

Os filtros são aplicados às worksheets que utilizam a mesma fonte de dados.

### 11.3 KPIs

Foram implementados quatro cards de indicadores:

- `WS01 - KPI Matrículas`;
- `WS02 - KPI Docentes`;
- `WS03 - KPI Escolas Ativas`;
- `WS04 - KPI Salas Utilizadas`.

Valores de referência para 2025:

| Indicador | Valor |
| --- | ---: |
| Matrículas | 46.018.380 |
| Docentes | 2.992.045 |
| Escolas Ativas | 180.540 |
| Salas Utilizadas | 1.646.884 |

Os cards utilizam fundo `#F5F5F5`, mantendo destaque visual em relação às áreas analíticas.

### 11.4 Visualizações

Foram implementadas quatro visualizações em barras horizontais:

- `WS05 - Matrículas por Região`;
- `WS06 - Matrículas por Rede`;
- `WS07 - Escolas Ativas por Dependência`;
- `WS08 - Escolas Ativas por Localização`.

As barras utilizam a cor:

`#4E79A7`

com opacidade de aproximadamente `90%`.

Foi adotada uma única cor principal para evitar que cores diferentes sejam interpretadas como categorias ou significados analíticos inexistentes.

Os títulos técnicos das worksheets não são exibidos no dashboard. Cada visualização possui título amigável específico.

Os rótulos de campo redundantes foram ocultados, mantendo a possibilidade de ordenação das categorias pela medida apresentada.

### 11.5 Layout e padronização

Foram utilizados containers horizontais flutuantes para organizar:

- KPIs;
- primeira linha de visualizações;
- segunda linha de visualizações.

Os containers principais possuem alinhamento horizontal consistente.

Padrões adotados:

- margem lateral principal próxima de `20 px`;
- espaçamento vertical consistente entre os blocos;
- bordas discretas;
- fundo branco nas áreas analíticas;
- KPIs com fundo cinza claro;
- título alinhado à esquerda;
- filtros agrupados na parte superior sem associação visual direta com os cards de KPI.

### 11.6 Fonte e período

O rodapé apresenta:

`Fonte: INEP — Censo Escolar | Período analisado: 2019–2025`

### 11.7 Validação funcional

Foram realizados testes de consistência dos indicadores e filtros.

Para 2024, o dashboard retornou:

| Indicador | Valor esperado |
| --- | ---: |
| Matrículas | 47.088.922 |
| Docentes | 2.939.002 |
| Escolas Ativas | 181.065 |
| Salas Utilizadas | 1.608.074 |

Os valores coincidiram com a camada analítica previamente validada.

Também foram testados filtros combinados envolvendo:

- Ano;
- Região;
- UF;
- Rede.

Foi validado o comportamento encadeado:

`Região → UF → demais visualizações`

Também foram realizadas verificações de reconciliação entre totais e segmentações, incluindo:

- Pública + Privada = total de Matrículas;
- Urbana + Rural = total de Escolas Ativas;
- dependências administrativas = total de Escolas Ativas;
- soma das regiões = total de Matrículas.

O dashboard foi salvo com o estado inicial:

`2025 | Todas as Regiões | Todas as UFs | Todas as Redes`

O recurso nativo de Reverter do Tableau pode ser utilizado para retornar ao estado salvo da visualização.

---

## 12. Dashboard Geografia e Administração

Foi implementado o dashboard:

`D03 - Geografia e Administração`

O objetivo da tela é permitir análise territorial das matrículas e exploração da estrutura administrativa das escolas brasileiras.

### 12.1 Estrutura

O dashboard mantém o padrão visual definido para o projeto:

- layout desktop `1200 × 800`;
- título e subtítulo;
- filtros superiores;
- bloco principal de análise geográfica;
- bloco inferior de estrutura administrativa;
- rodapé com fonte e período.

### 12.2 Filtros

Foram disponibilizados:

- Ano;
- Rede;
- Dependência Administrativa;
- Localização.

Estado padrão:

`2025 | Todas as Redes | Todas as Dependências | Todas as Localizações`

Os filtros são aplicados às worksheets que utilizam a mesma fonte de dados.

### 12.3 Análise geográfica

Foram criadas:

- `WS09 - Mapa Matrículas por UF`;
- `WS10 - Matrículas por UF`.

O mapa utiliza:

- Estado como dimensão geográfica;
- País = Brasil como contexto de geocodificação;
- `SUM(Matrículas)` como medida;
- mapa preenchido com escala sequencial de azul.

O ranking apresenta as 27 UFs ordenadas de forma decrescente pelo total de matrículas.

Valores de referência para 2025 incluem:

| UF | Matrículas |
| --- | ---: |
| SP | 9.600.318 |
| MG | 4.220.829 |
| BA | 3.345.058 |
| RJ | 3.319.771 |

O ranking mantém todas as UFs disponíveis com rolagem vertical.

### 12.4 Interação do mapa

Foi configurada uma ação de filtro no dashboard.

Ao selecionar uma UF no mapa, são filtradas apenas:

- `WS06 - Matrículas por Rede`;
- `WS07 - Escolas Ativas por Dependência`.

O ranking por UF permanece com contexto nacional, permitindo comparar o estado selecionado com as demais UFs.

Ao limpar a seleção do mapa, os gráficos administrativos retornam à visão completa.

Foi adicionada ao mapa a orientação:

`Clique em um estado para detalhar os gráficos abaixo`

### 12.5 Estrutura administrativa

O bloco inferior utiliza:

- `WS06 - Matrículas por Rede`;
- `WS07 - Escolas Ativas por Dependência`.

As visualizações mantêm o padrão definido no Panorama Geral:

- barras horizontais;
- cor `#4E79A7`;
- aproximadamente 90% de opacidade;
- sem borda nas barras;
- títulos amigáveis;
- rótulos de valores visíveis.

### 12.6 Layout

O bloco geográfico foi organizado com aproximadamente:

- 65% da largura para o mapa;
- 35% para o ranking.

A seção administrativa utiliza divisão aproximada de 50% para cada visualização.

O dashboard mantém alinhamento, bordas, espaçamentos e tipografia consistentes com `D01 - Panorama Geral`.

### 12.7 Validação

Foram validados:

- funcionamento dos filtros globais;
- consistência entre mapa e ranking;
- ordenação das UFs;
- ação de seleção do mapa;
- retorno à visão nacional após limpar a seleção;
- atualização dos gráficos administrativos conforme UF selecionada.

O refinamento específico de enquadramento e zoom do mapa será tratado separadamente como melhoria visual.

---

## 13. Dashboard Infraestrutura Escolar

Foi implementado o dashboard:

`D04 - Infraestrutura Escolar`

O objetivo da tela é analisar a disponibilidade de recursos de infraestrutura nas escolas em atividade e permitir comparação entre as redes Pública e Privada.

### 13.1 Estrutura

O dashboard mantém o padrão visual do projeto:

- layout desktop `1200 × 800`;
- título e subtítulo;
- filtros superiores;
- visão geral dos indicadores de infraestrutura;
- análise detalhada por Rede;
- rodapé com fonte e período analisado.

### 13.2 Filtros

Foram disponibilizados:

- Ano;
- Região;
- UF;
- Rede;
- Localização.

Estado padrão:

`2025 | Todas as Regiões | Todas as UFs | Todas as Redes | Todas as Localizações`

O filtro de UF permanece dependente do contexto geográfico selecionado por Região.

### 13.3 Indicadores de infraestrutura

A worksheet:

`WS11 - Infraestrutura Geral`

apresenta 11 indicadores:

- Água Potável;
- Energia em Rede Pública;
- Esgoto em Rede Pública;
- Internet;
- Acessibilidade;
- Banheiro PNE;
- Biblioteca;
- Sala de Leitura;
- Laboratório de Informática;
- Laboratório de Ciências;
- Quadra de Esportes.

Os indicadores utilizam os campos calculados referentes somente às escolas em atividade.

Como os campos possuem valores `0/1`, os percentuais são calculados por:

`AVG(indicador)`

Valores nulos não são convertidos automaticamente para zero.

A escala dos gráficos foi fixada entre:

`0% e 100%`

permitindo comparação consistente entre diferentes filtros.

### 13.4 Ordem dos indicadores

Foi adotada ordem temática em vez de ordem alfabética:

1. serviços básicos;
2. conectividade e acessibilidade;
3. recursos e espaços pedagógicos.

Essa organização mantém indicadores relacionados próximos e evita que a posição dos itens dependa dos valores apresentados.

### 13.5 Comparação por Rede

A worksheet:

`WS12 - Infraestrutura por Rede`

compara:

- Pública;
- Privada.

Inicialmente foram avaliadas múltiplas formas de apresentação dos 11 indicadores simultaneamente.

A versão final utiliza somente um indicador por vez, permitindo maior legibilidade e reduzindo densidade visual.

Foi criado o parâmetro:

`Indicador de Infraestrutura`

e o campo calculado:

`Indicador Selecionado`

responsável por retornar o indicador correspondente à escolha atual.

A visualização utiliza:

`AVG(Indicador Selecionado)`

com escala fixa de `0% a 100%`.

### 13.6 Ação de parâmetro

Foi configurada uma ação de parâmetro no dashboard.

Origem:

`WS11 - Infraestrutura Geral`

Destino:

`Indicador de Infraestrutura`

Campo utilizado:

`Nomes de medida`

Ao selecionar uma barra na visão geral, o parâmetro é atualizado e a `WS12` passa automaticamente a detalhar aquele indicador.

Exemplo:

`Quadra de Esportes (%)`

resulta na comparação:

- Privada: `45,87%`;
- Pública: `38,62%`.

O título da worksheet também é dinâmico, apresentando o indicador selecionado.

Exemplo:

`Infraestrutura por Rede - Quadra de Esportes (%)`

### 13.7 Identidade visual

A visão geral utiliza:

- barras `#4E79A7`;
- aproximadamente 90% de opacidade;
- sem borda;
- rótulos percentuais.

Na comparação por Rede são utilizadas cores distintas porque representam categorias analíticas diferentes:

- Privada: azul;
- Pública: laranja.

### 13.8 Interação

A principal interação da tela segue o fluxo:

`Visão Geral → seleção do indicador → detalhamento por Rede`

Foi incluída orientação visual para indicar que os elementos da visão geral são interativos.

Dessa forma, não foi necessário manter um seletor de parâmetro separado no dashboard.

### 13.9 Validação

Foram testados:

- filtros de Ano;
- Região;
- UF;
- Rede;
- Localização;
- percentuais da visão geral;
- comparação Pública × Privada;
- ação de parâmetro;
- título dinâmico;
- alteração entre diferentes indicadores;
- manutenção da escala entre `0% e 100%`.

O comportamento funcional do dashboard foi validado antes da conclusão da etapa.

---

## 14. Dashboard Evolução Histórica

Foi implementado o dashboard:

`D02 - Evolução Histórica`

O objetivo da tela é apresentar a evolução dos principais indicadores educacionais ao longo do período de 2019 a 2025, permitindo também análises por diferentes recortes geográficos e administrativos.

### 14.1 Estrutura

O dashboard mantém o padrão visual do projeto:

- layout desktop `1200 × 800`;
- título principal do projeto;
- subtítulo específico da análise;
- filtros superiores;
- quatro gráficos de evolução histórica organizados em grade `2 × 2`;
- rodapé com fonte e período analisado.

Foram utilizadas as worksheets:

- `WS13 - Evolução de Matrículas`;
- `WS14 - Evolução de Docentes`;
- `WS15 - Evolução de Escolas Ativas`;
- `WS16 - Evolução de Salas Utilizadas`.

### 14.2 Indicadores analisados

Os quatro indicadores apresentados são:

- Matrículas;
- Docentes;
- Escolas Ativas;
- Salas Utilizadas.

Cada gráfico apresenta os sete anos disponíveis:

`2019 → 2020 → 2021 → 2022 → 2023 → 2024 → 2025`

Não foi incluído filtro de Ano no dashboard, pois o objetivo da tela é justamente preservar a visualização completa da série histórica.

### 14.3 Filtros

Foram disponibilizados:

- Região;
- UF;
- Rede;
- Localização.

Estado padrão:

`Todas as Regiões | Todas as UFs | Todas as Redes | Todas as Localizações`

O filtro de UF permanece contextualizado pela Região selecionada.

Os filtros atualizam simultaneamente os quatro gráficos históricos.

### 14.4 Escalas dos gráficos

Os eixos verticais utilizam:

- intervalo automático;
- zero não obrigatório.

Essa configuração permite que a escala seja recalculada conforme os filtros aplicados.

A decisão de não utilizar escalas fixas foi necessária porque valores absolutos podem variar significativamente entre Brasil, Regiões, UFs, Redes e Localizações.

O eixo permanece visível para evitar interpretação incorreta das variações.

### 14.5 Formatação numérica

Foi adotada formatação simplificada nos eixos:

- Matrículas: milhões;
- Docentes: milhões;
- Escolas Ativas: milhares;
- Salas Utilizadas: milhões.

A quantidade de casas decimais foi ajustada individualmente para preservar legibilidade sem excesso de informação.

### 14.6 Rótulos

Para reduzir poluição visual, os valores não são apresentados em todos os anos.

Foram mantidos rótulos apenas nas extremidades das linhas:

- primeiro ano: `2019`;
- último ano: `2025`.

Os anos intermediários permanecem disponíveis no eixo horizontal e nas informações da visualização.

### 14.7 Identidade visual

Os quatro gráficos utilizam:

- gráfico de linha;
- cor principal `#4E79A7`;
- fundo branco;
- bordas discretas;
- ausência de títulos redundantes nos eixos;
- espaçamento uniforme entre os blocos.

Os quatro gráficos foram organizados em dois contêineres horizontais, com distribuição uniforme das worksheets.

### 14.8 Validação

Foram validados:

- os sete anos da série histórica;
- valores dos indicadores;
- filtros de Região;
- relacionamento Região → UF;
- filtros de Rede;
- filtros de Localização;
- atualização simultânea dos quatro gráficos;
- adaptação automática dos eixos;
- manutenção dos rótulos apenas em 2019 e 2025.

Após os testes, os filtros foram retornados ao estado padrão.

O comportamento funcional e visual do dashboard foi considerado validado.