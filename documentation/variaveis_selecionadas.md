# Variáveis selecionadas

Este documento registra as variáveis selecionadas para utilização no projeto **Censo Escolar BI**, a partir das perguntas de negócio e indicadores definidos na M1 e dos resultados da exploração e avaliação de Data Quality realizadas na M3.

A seleção prioriza apenas os campos necessários para identificação das escolas, análises geográficas, segmentação administrativa, indicadores principais e infraestrutura escolar.

## Tabela Escola

### Identificação

* "NU_ANO_CENSO" — Ano de referência do Censo Escolar.
* "CO_ENTIDADE" — Código da entidade escolar e principal identificador utilizado no relacionamento entre as tabelas.
* "NO_ENTIDADE" — Nome da escola.

### Geografia

* "CO_REGIAO"
* "NO_REGIAO"
* "CO_UF"
* "SG_UF"
* "NO_UF"
* "CO_MUNICIPIO"
* "NO_MUNICIPIO"

Essas variáveis permitirão análises na hierarquia:

**Brasil → Região → UF → Município → Escola**

### Segmentação e controle

* "TP_DEPENDENCIA" — Dependência administrativa da escola.
* "TP_LOCALIZACAO" — Localização urbana ou rural.
* "TP_SITUACAO_FUNCIONAMENTO" — Situação de funcionamento da escola.

A variável "TP_DEPENDENCIA" será utilizada também para derivar análises entre rede pública e privada.

### Infraestrutura

* "IN_INTERNET"
* "IN_BIBLIOTECA"
* "IN_SALA_LEITURA"
* "IN_LABORATORIO_CIENCIAS"
* "IN_LABORATORIO_INFORMATICA"
* "IN_QUADRA_ESPORTES"
* "IN_BANHEIRO_PNE"
* "IN_ACESSIBILIDADE_INEXISTENTE"
* "IN_AGUA_POTAVEL"
* "IN_ESGOTO_REDE_PUBLICA"
* "IN_ENERGIA_REDE_PUBLICA"
* "QT_SALAS_UTILIZADAS"

As variáveis de infraestrutura possuem diferentes períodos de disponibilidade histórica. As restrições identificadas na análise de comparabilidade deverão ser consideradas no ETL e na construção das visualizações.

## Tabela Matrícula

* "NU_ANO_CENSO"
* "CO_ENTIDADE"
* "QT_MAT_BAS"

"QT_MAT_BAS" será utilizada como indicador principal da quantidade de matrículas da Educação Básica.

Os atributos geográficos e administrativos serão obtidos por meio do relacionamento com a tabela Escola.

## Tabela Docente

* "NU_ANO_CENSO"
* "CO_ENTIDADE"
* "QT_DOC_BAS"

"QT_DOC_BAS" será utilizada como indicador principal da quantidade de docentes da Educação Básica.

Assim como na tabela Matrícula, os atributos geográficos e administrativos serão obtidos a partir da tabela Escola.

## Variáveis não selecionadas inicialmente

Algumas variáveis analisadas durante a exploração não foram incluídas no escopo inicial.

Entre elas:

* "TP_CATEGORIA_ESCOLA_PRIVADA", por não ser necessária para a análise inicial entre rede pública e privada;
* "TP_LOCALIZACAO_DIFERENCIADA", por representar uma segmentação específica que não faz parte das perguntas de negócio inicialmente definidas;
* campos geográficos e cadastrais duplicados nas tabelas Matrícula e Docente, pois essas informações poderão ser obtidas por meio da tabela Escola.

Essas variáveis não foram descartadas definitivamente e poderão ser incorporadas futuramente caso novas necessidades analíticas sejam identificadas.

## Critérios utilizados

A seleção considerou:

* perguntas de negócio definidas na M1;
* indicadores planejados para o dashboard;
* necessidade de análises geográficas;
* análise da evolução histórica;
* disponibilidade das variáveis ao longo dos anos;
* qualidade dos dados;
* relacionamentos entre as tabelas;
* redução de redundância entre conjuntos de dados.

A lista poderá receber ajustes durante as etapas de ETL, modelagem e desenvolvimento do dashboard caso sejam identificadas novas necessidades analíticas.
