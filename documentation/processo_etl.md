# Processo e Regras de ETL

Este documento descreve o processo de ETL utilizado no projeto **Censo Escolar BI**, desde os arquivos originais disponibilizados pelo INEP até a geração das bases tratadas e consolidadas utilizadas nas etapas de modelagem e visualização.

## 1. Objetivo

O processo de ETL tem como objetivo transformar os arquivos originais do Censo Escolar em bases adequadas para análise histórica e utilização no Tableau, garantindo:

* preservação dos dados originais;
* rastreabilidade das transformações;
* reprodutibilidade do processo;
* consistência entre diferentes anos;
* tratamento documentado de problemas de qualidade;
* utilização apenas das variáveis necessárias ao projeto.

## 2. Princípio de preservação dos dados brutos

Os arquivos disponibilizados pelo INEP serão armazenados na pasta:

"data/raw/"

Os arquivos dessa pasta deverão ser preservados sem alterações.

Nenhum processo de limpeza, transformação, correção ou padronização deverá sobrescrever os arquivos originais.

Todos os resultados do processo de ETL serão gerados em:

"data/processed/"

## 3. Tabelas utilizadas

O processo utilizará inicialmente as seguintes tabelas do Censo Escolar:

* Escola;
* Matrícula;
* Docente.

A tabela Escola será utilizada como principal referência para informações cadastrais, geográficas, administrativas e de infraestrutura.

As tabelas Matrícula e Docente fornecerão os principais indicadores quantitativos e serão relacionadas à Escola por meio de:

* "NU_ANO_CENSO"
* "CO_ENTIDADE"

## 4. Variáveis utilizadas

As variáveis selecionadas para o projeto estão documentadas em:

"documentation/variaveis_selecionadas.md"

Durante o ETL, somente as variáveis necessárias para o projeto deverão ser mantidas nas bases analíticas, salvo campos auxiliares necessários às transformações e validações.

## 5. Fluxo do ETL

O processo será executado na seguinte sequência:

### 5.1 Leitura dos dados brutos

Carregar os arquivos originais do INEP diretamente da pasta "data/raw/".

Os arquivos deverão ser interpretados conforme a estrutura oficial do Censo Escolar, incluindo separador, codificação e tipos de dados adequados.

### 5.2 Seleção de variáveis

Manter apenas as variáveis necessárias ao projeto e os campos auxiliares utilizados durante o tratamento.

### 5.3 Padronização

Padronizar:

* nomes de campos, quando necessário;
* tipos de dados;
* categorias;
* códigos;
* estruturas diferentes entre anos.

A padronização deverá preservar o significado original dos dados.

### 5.4 Tratamento de valores ausentes

Valores ausentes deverão ser analisados considerando o contexto da variável.

Valores nulos não deverão ser automaticamente substituídos por zero.

Quando um valor ausente representar situação em que determinado campo não se aplica, essa condição deverá ser preservada ou tratada de forma específica.

### 5.5 Tratamento de valores especiais

Códigos especiais definidos pelo INEP deverão receber tratamento específico.

Valores utilizados como marcadores de situações especiais não poderão ser interpretados como valores quantitativos reais.

Exemplo:

"88888"

Esse valor é utilizado em determinadas variáveis quantitativas para indicar valores extremos segundo regras estabelecidas pelo INEP.

O tratamento deverá permitir distinguir:

* valor quantitativo válido;
* valor ausente;
* valor especial ou extremo.

### 5.6 Validação de chaves e duplicidades

Após as transformações, deverá ser verificada a unicidade dos registros.

A combinação lógica utilizada para identificação histórica das entidades será:

"NU_ANO_CENSO + CO_ENTIDADE"

Duplicidades deverão ser investigadas antes de qualquer remoção automática.

### 5.7 Criação de variáveis derivadas

Serão criadas variáveis auxiliares necessárias às análises, como classificações e agrupamentos derivados dos códigos oficiais.

As regras utilizadas para cada variável derivada deverão ser documentadas.

### 5.8 Validação pós-tratamento

Após cada etapa relevante deverão ser comparados, quando aplicável:

* quantidade de registros;
* quantidade de entidades;
* valores nulos;
* duplicidades;
* totais dos principais indicadores;
* distribuições de categorias.

Transformações não deverão alterar indicadores de forma inesperada.

### 5.9 Harmonização histórica

Antes da consolidação de diferentes anos, deverão ser consideradas as análises realizadas na etapa de comparabilidade histórica.

Variáveis:

* introduzidas posteriormente;
* descontinuadas;
* renomeadas;
* derivadas de forma diferente;
* ou submetidas a alterações conceituais

não deverão ser comparadas automaticamente entre todos os anos.

As regras de harmonização deverão respeitar o período de validade e o conceito de cada variável.

### 5.10 Consolidação histórica

Após a padronização e harmonização, os dados de diferentes anos poderão ser consolidados.

A consolidação deverá manter obrigatoriamente o campo:

"NU_ANO_CENSO"

para identificar o período de referência de cada registro.

### 5.11 Geração da base analítica

Ao final do processo serão geradas bases tratadas na pasta:

"data/processed/"

Essas bases servirão de entrada para a etapa de modelagem BI e posteriormente para o Tableau.

## 6. Organização dos scripts

Os scripts de ETL serão armazenados em:

"scripts/"

Cada script deverá possuir uma responsabilidade clara e evitar alterações diretas nos arquivos brutos.

Sempre que possível, o processo deverá ser reproduzível apenas pela execução dos scripts disponíveis no repositório.

## 7. Regras gerais

Durante o desenvolvimento do ETL deverão ser seguidas as seguintes regras:

* nunca sobrescrever arquivos em "data/raw/";
* não substituir automaticamente valores nulos por zero;
* não eliminar registros sem investigação prévia;
* não remover duplicidades automaticamente sem identificar sua origem;
* respeitar os códigos e definições oficiais do INEP;
* documentar tratamentos de valores especiais;
* preservar "NU_ANO_CENSO" e "CO_ENTIDADE";
* validar resultados antes e depois das transformações;
* considerar a comparabilidade histórica antes de consolidar anos;
* manter o processo reproduzível por scripts;
* registrar alterações relevantes na documentação do projeto.

## 8. Fluxo resumido

O processo de ETL seguirá o fluxo:

**Dados brutos → Seleção de variáveis → Padronização → Tratamento de valores → Validação de chaves → Variáveis derivadas → Validação → Harmonização histórica → Consolidação → Base analítica para BI**

## 9. Rastreabilidade

O processo deverá permitir identificar:

* qual arquivo original foi utilizado;
* quais regras foram aplicadas;
* qual script realizou cada transformação;
* qual base processada foi produzida;
* qual versão dos dados foi utilizada no Tableau.

As decisões metodológicas identificadas durante o ETL deverão ser registradas na documentação do projeto.
