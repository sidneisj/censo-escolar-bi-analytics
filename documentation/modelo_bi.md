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

## 3. Granularidade

A granularidade da base é:

`1 registro = 1 Escola × 1 Ano`

A chave analítica utilizada para representar essa combinação é:

`ID_ANO_ENTIDADE`

Essa chave é formada a partir de:

- `NU_ANO_CENSO`;
- `CO_ENTIDADE`.

Uma mesma escola pode, portanto, aparecer várias vezes na base histórica, desde que em anos diferentes.

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