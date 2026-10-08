# Processo e Regras de ETL

Este documento descreve o processo de ETL utilizado no projeto **Censo Escolar BI/Analytics**, desde os arquivos originais disponibilizados pelo INEP até a geração das bases tratadas e da base analítica consolidada utilizada no Tableau.

## 1. Objetivo

O processo de ETL tem como objetivo transformar os arquivos originais do Censo Escolar em dados adequados para análise histórica e utilização em Business Intelligence, garantindo:

* preservação dos dados originais;
* rastreabilidade das transformações;
* reprodutibilidade do processo;
* consistência entre diferentes anos;
* tratamento documentado de problemas de qualidade;
* comparabilidade histórica;
* utilização apenas das variáveis necessárias ao projeto.

O período analítico consolidado nesta versão compreende os anos de **2019 a 2025**.

## 2. Preservação dos dados brutos

Os arquivos originais disponibilizados pelo INEP são armazenados em:

`data/raw/`

Os dados dessa área são preservados sem alterações.

Os processos de limpeza, tratamento, padronização e consolidação não sobrescrevem os arquivos de origem.

Os resultados gerados pelo ETL são armazenados em:

`data/processed/`

Essa separação permite preservar a rastreabilidade entre os dados originais e os produtos derivados.

## 3. Tabelas utilizadas

O processo utiliza informações provenientes principalmente das tabelas:

* Escola;
* Matrícula;
* Docente.

A tabela Escola fornece as principais informações cadastrais, geográficas, administrativas e de infraestrutura.

As informações de Matrícula e Docente fornecem os indicadores quantitativos utilizados no modelo.

A integração lógica entre as informações considera:

* `NU_ANO_CENSO`;
* `CO_ENTIDADE`.

A combinação desses campos permite identificar uma escola dentro de determinado ano do Censo Escolar.

## 4. Variáveis utilizadas

As variáveis selecionadas para o projeto estão documentadas em:

`documentation/variaveis_selecionadas.md`

Durante o processo de ETL foram mantidas somente as variáveis necessárias ao modelo analítico, além de campos auxiliares utilizados para transformação e validação.

Essa abordagem reduz redundâncias e mantém a base final adequada às necessidades dos dashboards.

## 5. Fluxo do ETL

O processo foi estruturado nas seguintes etapas.

### 5.1 Leitura dos dados brutos

Os arquivos originais do INEP são carregados a partir da área:

`data/raw/`

A leitura considera as características dos arquivos oficiais, incluindo codificação, separador e tipos de dados.

### 5.2 Seleção de variáveis

São selecionadas as variáveis necessárias para:

* identificação;
* geografia;
* estrutura administrativa;
* indicadores quantitativos;
* infraestrutura escolar;
* validações do processo.

Campos sem utilização no escopo analítico atual não são mantidos na base final.

### 5.3 Padronização

Os dados dos diferentes anos são padronizados para permitir sua consolidação histórica.

O processo considera, quando necessário:

* nomes de campos;
* tipos de dados;
* categorias;
* códigos;
* estruturas diferentes entre anos.

A padronização preserva o significado original das informações.

### 5.4 Tratamento de valores ausentes

Os valores ausentes são analisados de acordo com a semântica de cada variável.

Valores nulos não são automaticamente convertidos para zero.

Essa distinção é especialmente importante nos indicadores de infraestrutura, pois ausência de informação não deve ser interpretada automaticamente como ausência do recurso analisado.

Quando um campo não se aplica ou não estava disponível em determinado período, essa condição é preservada no tratamento.

### 5.5 Tratamento de valores especiais

Códigos especiais definidos pelo INEP são tratados separadamente de valores quantitativos normais.

Um exemplo identificado durante a exploração é:

`88888`

Esse código é utilizado em determinadas variáveis quantitativas para representar situações específicas relacionadas aos limites definidos pelo INEP e não deve ser interpretado diretamente como um valor quantitativo comum.

O tratamento diferencia:

* valores quantitativos válidos;
* valores ausentes;
* códigos especiais;
* situações extremas definidas metodologicamente pelo INEP.

### 5.6 Validação de chaves e duplicidades

Durante o tratamento foram realizadas verificações de unicidade e duplicidade dos registros.

A identificação histórica utilizada considera:

`NU_ANO_CENSO + CO_ENTIDADE`

Duplicidades são investigadas antes de qualquer decisão de remoção ou consolidação.

Na base analítica final, a granularidade adotada é:

`Escola × Ano`

### 5.7 Criação de variáveis derivadas

Foram criadas variáveis auxiliares necessárias às análises e aos dashboards.

Entre os exemplos estão derivações utilizadas para:

* classificação de Rede em Pública e Privada;
* identificação de escolas em atividade;
* tratamento dos indicadores de infraestrutura;
* interpretação positiva do indicador de acessibilidade;
* construção das dimensões utilizadas no Tableau.

As regras de transformação são mantidas de forma rastreável no processo e na documentação técnica.

### 5.8 Validação pós-tratamento

Após as principais etapas do ETL foram realizadas verificações envolvendo, conforme aplicável:

* quantidade de registros;
* quantidade de entidades;
* valores nulos;
* duplicidades;
* unicidade das chaves;
* totais dos principais indicadores;
* distribuições de categorias;
* consistência dos indicadores de infraestrutura.

Os resultados dessas validações estão registrados em:

`documentation/exploracao/`

Transformações que alterassem os indicadores de forma inesperada deveriam ser investigadas antes da continuidade do processo.

### 5.9 Harmonização histórica

Antes da consolidação dos anos de 2019 a 2025, foi avaliada a comparabilidade das variáveis ao longo do tempo.

Foram consideradas situações como variáveis:

* introduzidas em anos posteriores;
* descontinuadas;
* renomeadas;
* alteradas estruturalmente;
* submetidas a mudanças conceituais.

Variáveis sem comparabilidade adequada não foram assumidas automaticamente como equivalentes ao longo de toda a série histórica.

As regras adotadas respeitam o período de disponibilidade e o significado de cada variável segundo a documentação do INEP.

### 5.10 Consolidação histórica

Após a seleção, padronização, tratamento e harmonização, as bases anuais foram consolidadas para o período:

`2019 a 2025`

O campo:

`NU_ANO_CENSO`

é preservado para identificar o período de referência de cada registro.

A consolidação resultou em uma estrutura histórica com granularidade:

`Escola × Ano`

### 5.11 Geração da base analítica

O processo resulta na base utilizada como fonte principal do Tableau:

`data/processed/censo_escolar_tableau_2019_2025.csv`

Essa base reúne as dimensões e métricas necessárias para as análises desenvolvidas no projeto.

A base final contém informações relacionadas a:

* identificação das escolas;
* geografia;
* estrutura administrativa;
* situação de funcionamento;
* matrículas;
* docentes;
* salas utilizadas;
* infraestrutura escolar.

## 6. Organização dos scripts

Os scripts utilizados nas etapas de exploração, validação, tratamento, padronização e consolidação são armazenados em:

`scripts/`

Cada script possui uma responsabilidade específica dentro do processo.

A execução por scripts permite maior reprodutibilidade e reduz a necessidade de intervenções manuais sobre os dados.

Os arquivos originais em `data/raw/` não são modificados pelos scripts de tratamento.

## 7. Regras gerais

As seguintes regras foram adotadas durante o processo de ETL:

* não sobrescrever arquivos em `data/raw/`;
* não substituir automaticamente valores nulos por zero;
* não eliminar registros sem investigação prévia;
* não remover duplicidades sem analisar sua origem;
* respeitar os códigos e definições oficiais do INEP;
* documentar o tratamento de valores especiais;
* preservar `NU_ANO_CENSO` e `CO_ENTIDADE`;
* validar os resultados das transformações;
* considerar a comparabilidade histórica antes da consolidação;
* manter o processo reproduzível por scripts;
* registrar evidências de qualidade e validação;
* manter rastreabilidade entre origem, transformação e consumo analítico.

## 8. Fluxo resumido

O processo implementado pode ser representado pelo fluxo:

**Dados brutos → Seleção de variáveis → Padronização → Tratamento de valores → Validação de chaves → Variáveis derivadas → Validação → Harmonização histórica → Consolidação → Base analítica para BI**

## 9. Rastreabilidade

O processo permite identificar:

* os dados originais utilizados;
* as variáveis selecionadas;
* as regras aplicadas;
* os scripts responsáveis pelas transformações;
* as evidências produzidas durante as validações;
* a base processada resultante;
* a versão utilizada no Tableau.

As evidências das etapas de exploração, qualidade e validação estão armazenadas principalmente em:

`documentation/exploracao/`

A base analítica utilizada na camada de visualização é:

`data/processed/censo_escolar_tableau_2019_2025.csv`

Essa estrutura busca manter rastreabilidade entre **fonte → tratamento → validação → modelo analítico → dashboard**.