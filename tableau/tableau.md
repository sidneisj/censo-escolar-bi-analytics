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