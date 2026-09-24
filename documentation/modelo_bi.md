# Modelo Analítico para BI

## 1. Objetivo

Este documento registra as decisões de modelagem adotadas para utilização dos dados do Censo Escolar no Tableau.

A modelagem tem como objetivo fornecer uma estrutura analítica simples, rastreável e adequada à construção de dashboards sobre a evolução da educação básica brasileira entre 2019 e 2025.

---

## 2. Estratégia de modelagem adotada

Para a primeira versão do projeto foi adotada uma **tabela analítica única e desnormalizada**.

A fonte utilizada pelo Tableau será:

`data/processed/censo_escolar_tableau_2019_2025.csv`

A base contém informações de:

- identificação da escola;
- ano do Censo Escolar;
- localização geográfica;
- dependência administrativa;
- rede pública ou privada;
- localização urbana ou rural;
- situação de funcionamento;
- infraestrutura escolar;
- quantidade de matrículas;
- quantidade de docentes;
- quantidade de salas utilizadas;
- variáveis derivadas para análise.

---

## 3. Fato, granularidade e chaves do modelo

### 3.1 Fato analítico

O evento analítico central do modelo representa a situação de uma escola em um determinado ano do Censo Escolar.

Cada registro reúne características dimensionais da escola e medidas quantitativas referentes ao respectivo ano.

Entre as principais medidas associadas ao registro estão:

- quantidade de matrículas;
- quantidade de docentes;
- quantidade de salas utilizadas;
- situação de funcionamento;
- indicadores de infraestrutura.

Embora o modelo físico utilize uma tabela analítica única, conceitualmente cada registro pode ser interpretado como um fato anual associado a uma escola.

---

### 3.2 Granularidade

A granularidade da base é:

`1 registro = 1 Escola × 1 Ano`

Isso significa que uma escola possui no máximo um registro para cada ano do período analisado.

O período atualmente disponível compreende:

`2019 a 2025`

Uma mesma escola pode aparecer em vários registros da base quando estiver presente em diferentes anos do Censo Escolar.

Por esse motivo, a quantidade total de registros da base histórica não representa a quantidade de escolas distintas existentes no Brasil.

---

### 3.3 Chave da escola

O campo:

`CO_ENTIDADE`

representa o código de identificação da escola utilizado pelo Censo Escolar.

Esse código identifica a entidade escolar, mas não é único na base histórica completa, pois uma mesma escola pode aparecer em diferentes anos.

Exemplo conceitual:

```text
CO_ENTIDADE | NU_ANO_CENSO
12345678    | 2023
12345678    | 2024
12345678    | 2025
```

Nesse caso existem três registros históricos, mas todos pertencem à mesma escola.

---

### 3.4 Chave temporal

O campo:

`NU_ANO_CENSO`

identifica o ano de referência do Censo Escolar.

Ele será utilizado como principal dimensão temporal do modelo.

A combinação do ano com o código da escola determina a granularidade da base.

---

### 3.5 Chave analítica

Para representar de forma única cada registro foi criada a chave:

`ID_ANO_ENTIDADE`

Sua formação segue a regra:

`NU_ANO_CENSO + "_" + CO_ENTIDADE`

Exemplo:

```text
2025_43145833
```

Essa chave identifica exclusivamente uma escola em determinado ano.

Durante o processo de ETL foi validado que:

- não existem valores nulos nessa chave;
- não existem duplicidades;
- cada combinação Escola × Ano corresponde a um único registro.

---

### 3.6 Comportamento temporal das escolas

Uma escola pode apresentar situações diferentes ao longo da série histórica.

O modelo preserva a situação registrada em cada ano por meio de:

`TP_SITUACAO_FUNCIONAMENTO`

e de sua descrição derivada:

`DS_SITUACAO_FUNCIONAMENTO`

As situações observadas no período são:

- Em Atividade;
- Paralisada;
- Extinta no ano do Censo.

Também foi criada a variável:

`FL_ESCOLA_ATIVA`

com a seguinte regra:

```text
1 = escola em atividade
0 = escola não ativa
```

Essa variável permite calcular diretamente a quantidade de escolas em atividade dentro de um determinado contexto temporal.

---

### 3.7 Implicações para contagem de escolas

A existência de vários anos exige atenção na contagem das escolas.

`COUNT(ID_ANO_ENTIDADE)`

representa a quantidade de registros Escola × Ano.

Já:

`COUNTD(CO_ENTIDADE)`

representa a quantidade de escolas distintas presentes no contexto da análise.

Esses conceitos não são equivalentes quando mais de um ano estiver selecionado.

Por exemplo, uma escola presente de 2019 a 2025 corresponde a:

- 7 registros Escola × Ano;
- 1 escola distinta.

Portanto, métricas relacionadas à quantidade de escolas deverão considerar explicitamente o contexto temporal utilizado no dashboard.

As regras definitivas de agregação serão documentadas na issue dedicada às métricas e regras de cálculo.

---

### 3.8 Medidas associadas à granularidade

As principais medidas quantitativas disponíveis no nível Escola × Ano são:

`QT_MAT_BAS`  
Quantidade de matrículas da educação básica associadas à escola naquele ano.

`QT_DOC_BAS`  
Quantidade de docentes da educação básica associada à escola naquele ano.

`QT_SALAS_UTILIZADAS`  
Quantidade de salas utilizadas pela escola naquele ano.

Essas medidas podem ser agregadas geograficamente ou por características administrativas, desde que seja preservado o contexto temporal adequado.

---

### 3.9 Integridade do grão

A granularidade foi validada durante a etapa de ETL para todos os anos de 2019 a 2025.

A base final possui:

- 1.545.901 registros Escola × Ano;
- nenhuma chave analítica nula;
- nenhuma chave analítica duplicada;
- período completo de 2019 a 2025.

Dessa forma, a estrutura está adequada para utilização como camada analítica do Tableau.

---

## 4. Abordagens avaliadas

### 4.1 Tabela analítica única

Consiste em disponibilizar para o Tableau uma única tabela contendo dimensões e medidas.

**Vantagens:**

- menor complexidade;
- ausência de relacionamentos físicos adicionais;
- facilidade de utilização no Tableau;
- menor risco de joins incorretos;
- maior facilidade de publicação e manutenção;
- adequada ao volume e à granularidade atuais;
- facilita a construção inicial do portfólio.

**Limitações:**

- repetição dos atributos dimensionais ao longo dos anos;
- arquivo maior do que um modelo normalizado;
- necessidade de atenção às regras de agregação em análises com múltiplos anos.

---

### 4.2 Modelo dimensional em estrela

Uma alternativa seria separar a base em uma tabela fato e diferentes dimensões, por exemplo:

- fato Censo Escolar;
- dimensão Escola;
- dimensão Tempo;
- dimensão Geografia;
- dimensão Dependência Administrativa;
- dimensão Localização.

Essa abordagem poderia ser útil em cenários com:

- maior volume de dados;
- múltiplas tabelas fato;
- diferentes granularidades;
- reutilização das dimensões em vários conjuntos de dados;
- ambiente corporativo de Data Warehouse.

Para o escopo atual, entretanto, essa estrutura aumentaria a complexidade do modelo sem gerar um benefício proporcional.

---

### 4.3 Modelo híbrido

Também foi considerada uma abordagem híbrida, mantendo parte das dimensões separadas e parte dos atributos na tabela analítica.

Neste momento essa alternativa também não apresenta vantagem significativa para o projeto.

---

## 5. Decisão

Foi escolhida a utilização de **uma tabela analítica única e desnormalizada** para consumo pelo Tableau.

A decisão considera que:

1. a granularidade já está consolidada em Escola × Ano;
2. as informações necessárias ao dashboard pertencem ao mesmo contexto analítico;
3. a base final possui aproximadamente 1,5 milhão de registros, volume compatível com o escopo do projeto;
4. as chaves e relacionamentos foram previamente validados durante o ETL;
5. o modelo reduz a complexidade de implementação no Tableau;
6. não existem, nesta primeira versão, múltiplas tabelas fato com granularidades diferentes.

---

## 6. Modelo conceitual

Mesmo utilizando uma tabela física única, os campos serão tratados conceitualmente como dimensões e medidas.

### Dimensões

Exemplos:

- Ano;
- Escola;
- Região;
- UF;
- Município;
- Rede;
- Dependência Administrativa;
- Localização;
- Situação de Funcionamento;
- características de infraestrutura.

### Medidas

Exemplos:

- Matrículas;
- Docentes;
- Salas utilizadas;
- quantidade de escolas;
- quantidade de escolas ativas;
- indicadores e percentuais derivados.

A definição detalhada das dimensões, hierarquias, métricas e regras de agregação será realizada nas próximas atividades da M5.

---

## 7. Evolução futura

A utilização de uma tabela única não impede a evolução futura do projeto.

Caso novas fontes ou granularidades sejam incorporadas, o modelo poderá evoluir para uma arquitetura dimensional.

Exemplos de possíveis expansões:

- dados por etapa de ensino;
- dados por turma;
- indicadores de desempenho educacional;
- IDEB;
- ENEM;
- informações socioeconômicas;
- dados financeiros;
- novas tabelas fato.

Nesse cenário, dimensões conformadas como Tempo, Escola e Geografia poderão ser reutilizadas em um modelo estrela.

---

## 8. Conclusão

Para o escopo atual do projeto, a tabela analítica única oferece o melhor equilíbrio entre simplicidade, rastreabilidade, desempenho e facilidade de utilização no Tableau.

A estratégia adotada mantém o modelo suficientemente simples para construção dos dashboards atuais, sem impedir uma futura evolução para uma arquitetura dimensional mais complexa.

---

## 9. Dimensões e hierarquias de análise

Mesmo utilizando uma tabela analítica única, os atributos do modelo são organizados conceitualmente em dimensões.

Essas dimensões serão utilizadas no Tableau para filtros, segmentações, agrupamentos, detalhamento e navegação entre diferentes níveis de análise.

---

### 9.1 Dimensão Tempo

A dimensão temporal é representada por:

`NU_ANO_CENSO`

O modelo contém dados anuais do período:

`2019 a 2025`

Como o Censo Escolar utilizado no projeto possui periodicidade anual, não serão criados níveis artificiais de trimestre, mês ou dia.

**Hierarquia:**

`Ano`

**Principais usos:**

- evolução histórica;
- comparação entre anos;
- cálculo de variações;
- filtros temporais;
- análise de tendências.

---

### 9.2 Dimensão Escola

A escola é identificada pelos campos:

- `CO_ENTIDADE`;
- `NO_ENTIDADE`.

`CO_ENTIDADE` representa o identificador da escola e `NO_ENTIDADE` representa o nome registrado no respectivo ano do Censo Escolar.

Como o modelo possui granularidade Escola × Ano, os atributos da escola devem ser interpretados dentro do contexto temporal do registro.

**Principais usos:**

- identificação individual de escolas;
- detalhamento das análises;
- quantidade de escolas distintas;
- consulta de características específicas de uma unidade escolar.

A dimensão Escola não terá uma hierarquia própria no escopo atual.

---

### 9.3 Dimensão Geografia

A dimensão geográfica é composta pelos campos:

- `CO_REGIAO`;
- `NO_REGIAO`;
- `CO_UF`;
- `SG_UF`;
- `NO_UF`;
- `CO_MUNICIPIO`;
- `NO_MUNICIPIO`.

A principal hierarquia geográfica do projeto será:

`Brasil → Região → UF → Município`

O nível Brasil representa o total nacional e não necessita de uma coluna própria na base.

No Tableau, essa hierarquia permitirá navegar progressivamente do panorama nacional até o nível municipal.

**Principais usos:**

- comparação entre regiões;
- comparação entre estados;
- análises municipais;
- mapas;
- filtros geográficos;
- detalhamento hierárquico.

Para identificação técnica deverão ser priorizados os códigos geográficos, enquanto os nomes serão utilizados para apresentação.

---

### 9.4 Dimensão Administrativa

A estrutura administrativa das escolas será representada por:

- `TP_DEPENDENCIA`;
- `DS_DEPENDENCIA`;
- `DS_REDE`.

As categorias de dependência administrativa são:

- Federal;
- Estadual;
- Municipal;
- Privada.

A variável `DS_REDE` consolida essas categorias em:

- Pública;
- Privada.

Será utilizada a seguinte hierarquia conceitual:

`Rede → Dependência Administrativa`

Exemplo:

```text
Pública
├── Federal
├── Estadual
└── Municipal

Privada
└── Privada
```

**Principais usos:**

- comparação entre redes pública e privada;
- participação das diferentes dependências administrativas;
- evolução das matrículas por rede;
- análise de infraestrutura segundo dependência.

---

### 9.5 Dimensão Localização

A localização da escola é representada por:

- `TP_LOCALIZACAO`;
- `DS_LOCALIZACAO`.

As categorias disponíveis são:

- Urbana;
- Rural.

Essa dimensão será utilizada de forma independente, sem necessidade de hierarquia.

**Principais usos:**

- comparação urbano × rural;
- filtros;
- análise de infraestrutura;
- distribuição de escolas;
- comparação de matrículas e docentes.

---

### 9.6 Dimensão Situação de Funcionamento

A situação da escola é representada por:

- `TP_SITUACAO_FUNCIONAMENTO`;
- `DS_SITUACAO_FUNCIONAMENTO`;
- `FL_ESCOLA_ATIVA`.

As situações observadas na série histórica são:

- Em Atividade;
- Paralisada;
- Extinta no ano do Censo.

`FL_ESCOLA_ATIVA` será utilizado como indicador auxiliar para identificação das escolas em atividade.

Essa dimensão não possui hierarquia.

**Principais usos:**

- separar escolas ativas e não ativas;
- acompanhar quantidade de escolas em funcionamento;
- evitar inclusão indevida de escolas paralisadas ou extintas em determinados indicadores;
- analisar mudanças na situação das unidades escolares.

---

### 9.7 Dimensão Infraestrutura

As características de infraestrutura escolar são representadas por indicadores binários:

- `IN_INTERNET`;
- `IN_BIBLIOTECA`;
- `IN_SALA_LEITURA`;
- `IN_LABORATORIO_CIENCIAS`;
- `IN_LABORATORIO_INFORMATICA`;
- `IN_QUADRA_ESPORTES`;
- `IN_BANHEIRO_PNE`;
- `IN_ACESSIBILIDADE_INEXISTENTE`;
- `IN_AGUA_POTAVEL`;
- `IN_ESGOTO_REDE_PUBLICA`;
- `IN_ENERGIA_REDE_PUBLICA`.

De forma geral:

`1 = característica presente`

`0 = característica ausente`

Valores `NA` devem permanecer diferenciados de zero, pois podem representar situações não aplicáveis ou ausência de informação conforme a estrutura dos microdados.

Os campos de infraestrutura não formam uma hierarquia entre si.

Cada indicador representa uma característica independente da escola.

**Principais usos:**

- percentual de escolas com determinada infraestrutura;
- comparação territorial;
- comparação entre redes;
- comparação urbano × rural;
- evolução histórica das condições de infraestrutura.

O campo `IN_ACESSIBILIDADE_INEXISTENTE` exige atenção especial na interpretação, pois sua lógica é inversa aos demais indicadores: o valor positivo indica inexistência de recursos de acessibilidade.

---

### 9.8 Hierarquias oficiais do modelo

As hierarquias definidas para utilização no Tableau são:

#### Geográfica

`Brasil → Região → UF → Município`

#### Administrativa

`Rede → Dependência Administrativa`

#### Temporal

`Ano`

As demais dimensões serão utilizadas como atributos independentes de filtro e segmentação.

---

### 9.9 Campos de código e descrição

Sempre que existirem campos de código e descrição, os códigos serão mantidos no modelo para garantir:

- identificação inequívoca;
- rastreabilidade;
- consistência de relacionamentos;
- possibilidade de futuras integrações.

Os campos descritivos serão utilizados preferencialmente na interface do dashboard.

Exemplos:

`CO_UF` → identificação técnica

`NO_UF` / `SG_UF` → apresentação

`CO_MUNICIPIO` → identificação técnica

`NO_MUNICIPIO` → apresentação

`TP_DEPENDENCIA` → código oficial

`DS_DEPENDENCIA` → apresentação

---

### 9.10 Uso das dimensões no Tableau

As dimensões deverão permitir que os principais indicadores sejam analisados segundo diferentes perspectivas sem alterar a granularidade original da base.

Exemplo conceitual:

```text
Ano
  ↓
Região
  ↓
UF
  ↓
Município
  ↓
Rede
  ↓
Dependência
  ↓
Urbana / Rural
```

Essa sequência representa possibilidades de segmentação e não uma única hierarquia obrigatória.

Filtros poderão ser combinados conforme o objetivo de cada dashboard.

---

### 9.11 Resumo das dimensões

| Dimensão | Principais campos | Hierarquia |
|---|---|---|
| Tempo | `NU_ANO_CENSO` | Ano |
| Escola | `CO_ENTIDADE`, `NO_ENTIDADE` | — |
| Geografia | Região, UF, Município | Brasil → Região → UF → Município |
| Administrativa | `DS_REDE`, `DS_DEPENDENCIA` | Rede → Dependência |
| Localização | `DS_LOCALIZACAO` | — |
| Situação | `DS_SITUACAO_FUNCIONAMENTO`, `FL_ESCOLA_ATIVA` | — |
| Infraestrutura | indicadores `IN_*` selecionados | — |

As dimensões definidas atendem às perguntas analíticas estabelecidas para o projeto e serão utilizadas como base para definição das métricas e KPIs na próxima etapa.

---

## 10. Métricas e KPIs do dashboard

As métricas e KPIs foram definidos a partir das perguntas analíticas estabelecidas para o projeto e das informações disponíveis na base consolidada de 2019 a 2025.

Os indicadores foram divididos em:

- KPIs principais;
- métricas de apoio;
- indicadores de infraestrutura;
- métricas de evolução histórica.

---

### 10.1 Princípio de contexto temporal

A base possui granularidade:

`Escola × Ano`

Por esse motivo, os principais KPIs quantitativos devem sempre ser interpretados dentro de um contexto temporal.

No dashboard, os valores em destaque deverão representar preferencialmente um único ano selecionado.

Exemplo:

`Ano selecionado = 2025`

Nesse contexto, os KPIs representam a situação observada no Censo Escolar de 2025.

Ao analisar vários anos simultaneamente, a soma de determinados indicadores representa acumulados de registros anuais e não necessariamente uma quantidade única de entidades.

As regras detalhadas de agregação serão formalizadas na issue específica de cálculos do Tableau.

---

## 10.2 KPI — Total de Matrículas

**Nome de apresentação:** Matrículas

**Campo de origem:**

`QT_MAT_BAS`

**Definição:**

Quantidade total de matrículas da educação básica registradas nas escolas dentro do contexto selecionado.

**Agregação básica:**

`SUM(QT_MAT_BAS)`

**Segmentações aplicáveis:**

- Ano;
- Região;
- UF;
- Município;
- Rede;
- Dependência Administrativa;
- Localização.

**Interpretação:**

Representa o volume de matrículas da educação básica no recorte selecionado.

**Valor de controle para 2025:**

`46.018.380`

---

## 10.3 KPI — Total de Docentes

**Nome de apresentação:** Docentes

**Campo de origem:**

`QT_DOC_BAS`

**Definição:**

Quantidade total de docentes da educação básica associada às escolas dentro do contexto selecionado.

**Agregação básica:**

`SUM(QT_DOC_BAS)`

**Segmentações aplicáveis:**

- Ano;
- Região;
- UF;
- Município;
- Rede;
- Dependência Administrativa;
- Localização.

**Interpretação:**

Representa o total de docentes registrado no recorte analisado.

**Valor de controle para 2025:**

`2.992.045`

---

## 10.4 KPI — Escolas Ativas

**Nome de apresentação:** Escolas Ativas

**Campo de origem:**

`FL_ESCOLA_ATIVA`

**Definição:**

Quantidade de registros de escolas classificadas como em atividade no respectivo ano do Censo Escolar.

**Agregação básica em contexto de um único ano:**

`SUM(FL_ESCOLA_ATIVA)`

**Segmentações aplicáveis:**

- Ano;
- Região;
- UF;
- Município;
- Rede;
- Dependência Administrativa;
- Localização.

**Interpretação:**

Representa a quantidade de escolas em funcionamento no período e recorte selecionados.

**Valor de controle para 2025:**

`180.540`

Quando múltiplos anos forem analisados simultaneamente, essa medida deverá ser interpretada como quantidade de registros Escola × Ano ativos e não como quantidade de escolas distintas existentes em todo o período.

---

## 10.5 KPI — Salas Utilizadas

**Nome de apresentação:** Salas Utilizadas

**Campo de origem:**

`QT_SALAS_UTILIZADAS`

**Definição:**

Quantidade total de salas utilizadas pelas escolas dentro do contexto selecionado.

**Agregação básica:**

`SUM(QT_SALAS_UTILIZADAS)`

**Segmentações aplicáveis:**

- Ano;
- Região;
- UF;
- Município;
- Rede;
- Dependência Administrativa;
- Localização.

**Interpretação:**

Representa a estrutura física utilizada pelas escolas no respectivo recorte.

**Valor de controle para 2025:**

`1.646.884`

---

## 10.6 Métrica — Escolas Registradas

**Nome de apresentação:** Escolas Registradas

**Campo principal:**

`ID_ANO_ENTIDADE`

**Definição:**

Quantidade de registros de entidades escolares presentes no Censo dentro do contexto temporal selecionado, independentemente da situação de funcionamento.

Em um único ano, pode ser calculada pela contagem dos registros da base.

**Uso:**

Essa métrica será utilizada principalmente para contextualização e análise da situação de funcionamento.

Ela não deverá substituir o KPI de Escolas Ativas quando o objetivo for representar escolas efetivamente em funcionamento.

---

## 10.7 Métricas por Rede

A variável:

`DS_REDE`

permite segmentar os principais indicadores entre:

- Pública;
- Privada.

As métricas aplicáveis incluem:

- Matrículas por Rede;
- Docentes por Rede;
- Escolas Ativas por Rede;
- Salas Utilizadas por Rede;
- participação percentual de cada rede.

Essas métricas permitirão analisar a distribuição dos recursos e da população escolar entre os setores público e privado.

---

## 10.8 Métricas por Dependência Administrativa

A variável:

`DS_DEPENDENCIA`

permite analisar os indicadores segundo:

- Federal;
- Estadual;
- Municipal;
- Privada.

Poderão ser analisados:

- Matrículas;
- Docentes;
- Escolas Ativas;
- Salas Utilizadas;
- participação percentual de cada dependência.

---

## 10.9 Métricas por Localização

A variável:

`DS_LOCALIZACAO`

permite comparar:

- Urbana;
- Rural.

Serão analisados, conforme o contexto:

- Matrículas;
- Docentes;
- Escolas Ativas;
- Salas Utilizadas;
- infraestrutura escolar.

Essa dimensão será especialmente relevante para identificar diferenças territoriais na estrutura educacional.

---

## 10.10 Indicadores de Infraestrutura

Os indicadores de infraestrutura deverão representar a proporção de escolas que possuem determinada característica.

Os campos disponíveis são:

- `IN_INTERNET`;
- `IN_BIBLIOTECA`;
- `IN_SALA_LEITURA`;
- `IN_LABORATORIO_CIENCIAS`;
- `IN_LABORATORIO_INFORMATICA`;
- `IN_QUADRA_ESPORTES`;
- `IN_BANHEIRO_PNE`;
- `IN_ACESSIBILIDADE_INEXISTENTE`;
- `IN_AGUA_POTAVEL`;
- `IN_ESGOTO_REDE_PUBLICA`;
- `IN_ENERGIA_REDE_PUBLICA`.

Para os indicadores cuja lógica é positiva:

`1 = possui`

`0 = não possui`

A métrica principal será:

`Percentual de escolas com o recurso`

O denominador deverá considerar escolas em atividade e registros com informação válida para o respectivo indicador.

Valores `NA` não deverão ser tratados automaticamente como ausência do recurso.

---

### 10.10.1 Exemplo conceitual

Para Internet:

**Quantidade de escolas com Internet**

Soma dos registros em que:

`IN_INTERNET = 1`

**Percentual de escolas com Internet**

Quantidade de escolas ativas com `IN_INTERNET = 1` dividida pela quantidade de escolas ativas com informação válida em `IN_INTERNET`.

O mesmo princípio será aplicado aos demais indicadores de infraestrutura.

---

### 10.10.2 Acessibilidade

O campo:

`IN_ACESSIBILIDADE_INEXISTENTE`

possui interpretação inversa aos demais indicadores.

Nesse campo:

`1 = inexistência de recursos de acessibilidade`

Por isso, ele não deverá ser apresentado diretamente como “escolas com acessibilidade”.

Caso seja necessário apresentar um indicador positivo de acessibilidade, deverá ser criado um campo calculado específico no Tableau, respeitando os valores válidos e ausentes.

A regra será formalizada na etapa de campos calculados.

---

## 10.11 Métricas de Evolução Histórica

Os principais indicadores deverão permitir análise ao longo de 2019 a 2025.

Serão analisadas as evoluções de:

- Matrículas;
- Docentes;
- Escolas Ativas;
- Salas Utilizadas;
- indicadores selecionados de infraestrutura.

A análise histórica poderá utilizar:

- valor absoluto anual;
- diferença absoluta em relação ao ano anterior;
- variação percentual em relação ao ano anterior.

Exemplo conceitual:

`Variação % de Matrículas`

compara o total de matrículas de um ano com o total do ano imediatamente anterior.

A fórmula e o comportamento desses cálculos no Tableau serão definidos na issue de regras de agregação e campos calculados.

---

## 10.12 Métricas Geográficas

Todos os principais KPIs poderão ser analisados segundo a hierarquia:

`Brasil → Região → UF → Município`

Isso permitirá responder questões como:

- quais regiões concentram mais matrículas;
- como o número de escolas evolui por estado;
- quais municípios apresentam determinada característica de infraestrutura;
- como as redes pública e privada se distribuem territorialmente.

Os valores nacionais deverão corresponder à agregação dos registros presentes na base, sem criação de linhas adicionais representando o Brasil.

---

## 10.13 KPIs principais do dashboard

Os indicadores prioritários para apresentação em destaque serão:

| KPI | Campo principal | Agregação básica |
|---|---|---|
| Matrículas | `QT_MAT_BAS` | Soma |
| Docentes | `QT_DOC_BAS` | Soma |
| Escolas Ativas | `FL_ESCOLA_ATIVA` | Soma em contexto anual |
| Salas Utilizadas | `QT_SALAS_UTILIZADAS` | Soma |

Esses KPIs formarão o panorama principal do sistema educacional no período selecionado.

---

## 10.14 Indicadores analíticos complementares

Além dos KPIs principais, o dashboard poderá utilizar:

- distribuição de matrículas por rede;
- distribuição de escolas por dependência administrativa;
- distribuição urbano × rural;
- participação percentual por categoria;
- percentual de escolas com infraestrutura;
- evolução anual dos principais indicadores;
- comparações entre regiões, estados e municípios.

Esses indicadores não alteram a granularidade do modelo e serão derivados das medidas e dimensões já existentes.

---

## 10.15 Resumo das regras

As principais regras estabelecidas são:

1. KPIs principais devem possuir contexto temporal explícito;
2. matrículas, docentes e salas utilizadas utilizam soma;
3. escolas ativas utilizam `FL_ESCOLA_ATIVA`;
4. escolas distintas exigem atenção quando vários anos estiverem selecionados;
5. indicadores de infraestrutura devem considerar apenas respostas válidas;
6. `NA` não deve ser convertido automaticamente em zero;
7. indicadores históricos devem preservar a comparabilidade definida durante o ETL;
8. cálculos de variação e percentuais serão formalizados na próxima etapa.