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