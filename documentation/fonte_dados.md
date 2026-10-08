# Fonte dos dados

## Censo Escolar da Educação Básica

Os dados utilizados neste projeto são provenientes dos **Microdados do Censo Escolar da Educação Básica**, disponibilizados oficialmente pelo **Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (INEP)**.

## Fonte oficial

**Instituição:** Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira — INEP

**Conjunto de dados:** Microdados do Censo Escolar da Educação Básica

**Período analisado:** 2019 a 2025

**Página oficial:**
https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar

## Bases utilizadas

O projeto utiliza dados do Censo Escolar referentes ao período de **2019 a 2025**.

Durante as etapas iniciais de exploração e definição do modelo analítico, foram analisadas principalmente informações provenientes das tabelas de:

* Escola;
* Matrícula;
* Docente.

Para o ano de 2025, os arquivos utilizados como referência foram:

* `Tabela_Escola_2025_V2.csv`;
* `Tabela_Matricula_2025_V2.csv`;
* `Tabela_Docente_2025_V2.csv`.

A análise de comparabilidade histórica permitiu identificar e selecionar as variáveis adequadas para utilização ao longo do período de 2019 a 2025.

## Versão e documentação oficial

A documentação técnica utilizada como referência foi obtida a partir do pacote oficial dos **Microdados do Censo Escolar 2025**, disponibilizado pelo INEP.

O pacote contém materiais complementares, incluindo:

* leia-me e orientações de utilização;
* dicionário de dados;
* questionários;
* documentos técnicos e metodológicos;
* arquivo de verificação de integridade MD5.

Parte dessa documentação oficial é mantida no repositório em:

`documentation/INEP/`

## Data de obtenção

**Data de obtenção da documentação e dos microdados de referência de 2025:** 18/09/2026

## Integridade e rastreabilidade

Os arquivos originais foram obtidos diretamente da fonte oficial e preservados sem alterações durante o processo de aquisição.

O pacote de 2025 disponibilizado pelo INEP contém o arquivo:

`md5_microdados_ed_basica_2025.txt`

utilizado como referência para verificação da integridade dos arquivos distribuídos.

Os dados originais são mantidos na área:

`data/raw/`

Os dados resultantes dos processos de tratamento, padronização, consolidação e preparação para análise são armazenados em:

`data/processed/`

A base analítica final utilizada no Tableau é:

`data/processed/censo_escolar_tableau_2019_2025.csv`

## Integração e consolidação

A variável:

`CO_ENTIDADE`

é utilizada como identificador da escola nas bases do Censo Escolar.

Para análise histórica, a combinação entre escola e ano permite identificar cada observação da base consolidada, cuja granularidade final é:

`Escola × Ano`

O processo de consolidação preserva as dimensões e indicadores necessários às análises geográficas, administrativas, de infraestrutura e evolução histórica realizadas no projeto.

## Comparabilidade histórica

Antes da consolidação das bases de 2019 a 2025, foram avaliadas alterações de disponibilidade, nomenclatura e significado das variáveis ao longo dos anos.

As evidências dessas análises estão registradas em arquivos da pasta:

`documentation/exploracao/`

incluindo verificações de:

* disponibilidade das variáveis;
* comparabilidade histórica;
* categorias;
* valores ausentes;
* granularidade;
* indicadores;
* validações da base consolidada.

## Observação

As regras, definições e orientações metodológicas fornecidas pelo INEP foram consideradas durante as etapas de exploração, qualidade, tratamento, modelagem e construção das análises.

A documentação técnica do projeto busca preservar a rastreabilidade entre os dados de origem, as transformações realizadas e a base analítica utilizada nos dashboards.