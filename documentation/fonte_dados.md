# Fonte dos dados

## Censo Escolar da Educação Básica

Os dados utilizados neste projeto são provenientes dos **Microdados do Censo Escolar da Educação Básica**, disponibilizados oficialmente pelo **Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (INEP)**.

### Fonte oficial

**Instituição:** Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira — INEP

**Conjunto de dados:** Microdados do Censo Escolar da Educação Básica

**Ano de referência:** 2025

**Página oficial:**
https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar

### Arquivos selecionados

Para a primeira versão do projeto foram selecionados os seguintes arquivos:

* `Tabela_Escola_2025_V2.csv`
* `Tabela_Matricula_2025_V2.csv`
* `Tabela_Docente_2025_V2.csv`

As demais tabelas disponibilizadas no pacote não fazem parte do escopo inicial, mas poderão ser utilizadas em etapas futuras caso novas necessidades de análise sejam identificadas.

### Versão e documentação

Os arquivos foram obtidos a partir do pacote oficial de Microdados do Censo Escolar 2025 disponibilizado pelo INEP.

O pacote também contém documentação complementar, incluindo:

* manual do usuário;
* dicionário de dados;
* questionários;
* documentos técnicos e metodológicos;
* arquivo de verificação de integridade MD5.

### Data de obtenção

**Data de obtenção:** 18/09/2026

### Integridade e rastreabilidade

Os arquivos originais foram obtidos diretamente da fonte oficial e serão preservados sem alterações.

O pacote disponibilizado pelo INEP contém o arquivo `md5_microdados_ed_basica_2025.txt`, utilizado para verificação da integridade dos arquivos distribuídos.

Os dados originais serão mantidos na área `data/raw/`, enquanto os dados submetidos a processos de tratamento e transformação serão armazenados posteriormente em `data/processed/`.

### Integração das bases

As tabelas selecionadas são organizadas por estabelecimento de ensino e podem ser relacionadas por meio da variável `CO_ENTIDADE`, utilizada como chave de integração entre as diferentes bases do Censo Escolar.

### Observação

A documentação e as regras metodológicas fornecidas pelo INEP serão consideradas durante as etapas de exploração, qualidade, tratamento e modelagem dos dados.
