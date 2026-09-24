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