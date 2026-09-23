# Censo Escolar BI/Analytics

Projeto de Business Intelligence desenvolvido a partir de dados públicos do **Censo Escolar**, disponibilizados pelo Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (INEP).

O projeto tem como objetivo transformar dados educacionais públicos em informações analíticas por meio de processos de tratamento, modelagem e visualização de dados, utilizando **Tableau** como ferramenta de BI.

## 🎯 Objetivo

Desenvolver um dashboard analítico que permita explorar informações da Educação Básica brasileira, possibilitando análises por diferentes dimensões, como:

* evolução ao longo do tempo;
* localização geográfica;
* Unidade da Federação;
* município;
* características das escolas;
* matrículas;
* docentes.

## 📊 Fonte dos dados

Os dados utilizados neste projeto são provenientes dos **Microdados do Censo Escolar da Educação Básica**, disponibilizados oficialmente pelo Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (INEP).

**Ano de referência atual:** 2025

**Fonte oficial:**
https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar

Os dados são obtidos diretamente da fonte oficial e mantidos com rastreabilidade de origem, versão e data de obtenção. Os arquivos originais são preservados sem alterações, enquanto os dados tratados serão disponibilizados posteriormente na área `data/processed/`.

Para informações detalhadas sobre a origem, arquivos utilizados, documentação e integridade dos dados, consulte [`documentation/fonte_dados.md`](documentation/fonte_dados.md).

## 🛠️ Tecnologias

* **Tableau** — visualização e desenvolvimento do dashboard
* **Git / GitHub** — versionamento, documentação e acompanhamento do projeto
* **SQL / Python** — tratamento e transformação de dados, conforme necessidade das etapas
* **CSV** — formato dos dados disponibilizados pelo INEP

## 📁 Estrutura do projeto

```text
censo-escolar-bi/
│
├── data/
│   ├── raw/              # Dados originais
│   └── processed/        # Dados tratados
│
├── documentation/        # Documentação e referências
│
├── scripts/              # Scripts de tratamento e transformação
│
├── tableau/              # Arquivos relacionados ao Tableau
│
└── README.md             # Documentação principal do projeto
```

## 🚧 Status do projeto

**Em desenvolvimento**

### Fases do projeto

* [x] **M1 — Definição do projeto**
* [x] **M2 — Fonte e aquisição dos dados**
* [x] **M3 — Exploração e qualidade dos dados**
* [x] **M4 — Tratamento e transformação**
* [ ] **M5 — Modelagem dos dados**
* [ ] **M6 — Desenvolvimento do dashboard**
* [ ] **M7 — Validação e documentação**
* [ ] **M8 — Publicação e apresentação**

Atualmente, o projeto encontra-se na **M2 — Fonte e aquisição dos dados**.

## 📌 Escopo atual

Para a primeira versão do projeto foram selecionadas inicialmente as seguintes bases do Censo Escolar:

* **Tabela Escola**
* **Tabela Matrícula**
* **Tabela Docente**

As demais bases poderão ser incorporadas posteriormente caso novas necessidades de análise sejam identificadas.

As bases do Censo Escolar são relacionadas por meio da variável `CO_ENTIDADE`.

## 📚 Documentação

As decisões, atividades e etapas de desenvolvimento são acompanhadas por meio do **GitHub Projects**, utilizando Issues e Milestones.

O histórico do projeto será mantido por meio de commits, documentação e demais artefatos produzidos durante o desenvolvimento.

---

**Projeto desenvolvido para fins de estudo, portfólio profissional e demonstração de práticas de Business Intelligence e análise de dados.**
