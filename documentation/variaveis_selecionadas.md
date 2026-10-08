# Variáveis selecionadas

Este documento registra as variáveis selecionadas e utilizadas no projeto **Censo Escolar BI/Analytics**, considerando as perguntas de negócio definidas na M1, as análises de qualidade da M3 e as decisões tomadas durante as etapas de tratamento, modelagem e construção dos dashboards.

A seleção priorizou os campos necessários para identificação das escolas, análises geográficas e administrativas, indicadores principais e infraestrutura escolar.

## Tabela Escola

### Identificação

* `NU_ANO_CENSO` — Ano de referência do Censo Escolar.
* `CO_ENTIDADE` — Código da entidade escolar e principal identificador da escola.
* `NO_ENTIDADE` — Nome da escola.

A combinação entre:

`NU_ANO_CENSO + CO_ENTIDADE`

é utilizada para representar a granularidade histórica:

`Escola × Ano`

### Geografia

* `CO_REGIAO`
* `NO_REGIAO`
* `CO_UF`
* `SG_UF`
* `NO_UF`
* `CO_MUNICIPIO`
* `NO_MUNICIPIO`

Essas variáveis suportam análises na hierarquia:

**Brasil → Região → UF → Município → Escola**

No Tableau, foram utilizadas principalmente as dimensões Região, UF, Estado e Município para filtros, hierarquias e análises geográficas.

### Segmentação e controle

* `TP_DEPENDENCIA` — Dependência administrativa da escola.
* `TP_LOCALIZACAO` — Localização urbana ou rural.
* `TP_SITUACAO_FUNCIONAMENTO` — Situação de funcionamento da escola.

A variável `TP_DEPENDENCIA` também é utilizada para a derivação da dimensão **Rede**, permitindo análises entre:

* Pública;
* Privada.

A variável `TP_SITUACAO_FUNCIONAMENTO` é utilizada na identificação das escolas em atividade, condição adotada em diferentes indicadores do modelo analítico.

### Infraestrutura

Foram selecionadas as seguintes variáveis:

* `IN_INTERNET`
* `IN_BIBLIOTECA`
* `IN_SALA_LEITURA`
* `IN_LABORATORIO_CIENCIAS`
* `IN_LABORATORIO_INFORMATICA`
* `IN_QUADRA_ESPORTES`
* `IN_BANHEIRO_PNE`
* `IN_ACESSIBILIDADE_INEXISTENTE`
* `IN_AGUA_POTAVEL`
* `IN_ESGOTO_REDE_PUBLICA`
* `IN_ENERGIA_REDE_PUBLICA`
* `QT_SALAS_UTILIZADAS`

Os indicadores de infraestrutura foram utilizados considerando somente escolas em atividade.

Para os campos binários, a lógica analítica preserva os valores válidos `0/1` e os valores nulos, evitando transformar ausência de informação automaticamente em resposta negativa.

A variável:

`IN_ACESSIBILIDADE_INEXISTENTE`

possui semântica inversa. Por esse motivo, foi utilizada para derivar um indicador positivo de acessibilidade no modelo analítico e no Tableau.

As diferenças de disponibilidade histórica das variáveis foram avaliadas antes da consolidação das bases de 2019 a 2025.

## Tabela Matrícula

Foram utilizadas:

* `NU_ANO_CENSO`
* `CO_ENTIDADE`
* `QT_MAT_BAS`

A variável:

`QT_MAT_BAS`

é utilizada como indicador de quantidade de matrículas da Educação Básica.

Os atributos geográficos e administrativos necessários à análise foram consolidados a partir das informações da escola durante o processo de tratamento e modelagem.

## Tabela Docente

Foram utilizadas:

* `NU_ANO_CENSO`
* `CO_ENTIDADE`
* `QT_DOC_BAS`

A variável:

`QT_DOC_BAS`

é utilizada como indicador de quantidade de docentes da Educação Básica.

Assim como em Matrícula, os atributos necessários às análises foram consolidados no modelo final em nível de Escola × Ano.

## Variáveis não incorporadas ao modelo analítico

Algumas variáveis avaliadas durante a exploração não foram incorporadas à versão atual do modelo.

Entre elas:

* `TP_CATEGORIA_ESCOLA_PRIVADA` — não necessária para o nível de análise adotado entre rede pública e privada;
* `TP_LOCALIZACAO_DIFERENCIADA` — representa uma segmentação específica não contemplada pelas perguntas analíticas da versão atual;
* campos geográficos e cadastrais redundantes existentes em diferentes conjuntos de dados — evitados para reduzir duplicação no modelo consolidado.

A exclusão dessas variáveis representa uma decisão de escopo da versão atual e não impede sua utilização em futuras evoluções do projeto.

## Critérios utilizados

A seleção das variáveis considerou:

* perguntas de negócio definidas na M1;
* indicadores utilizados nos dashboards;
* necessidade de análises geográficas e administrativas;
* análise da evolução histórica;
* disponibilidade das variáveis entre 2019 e 2025;
* qualidade e semântica dos dados;
* relacionamentos entre os conjuntos de dados;
* redução de redundância;
* adequação à granularidade final Escola × Ano;
* necessidade de rastreabilidade entre origem, transformação e visualização.

As decisões tomadas durante o ETL e a modelagem resultaram na base analítica consolidada utilizada pelo Tableau:

`data/processed/censo_escolar_tableau_2019_2025.csv`