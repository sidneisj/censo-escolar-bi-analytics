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

---

## 9. Hierarquias e campos calculados

Após a configuração inicial da fonte de dados, foram implementadas no Tableau Cloud as hierarquias e medidas calculadas definidas durante a etapa de modelagem analítica.

### 9.1 Hierarquia Geografia

Foi criada a hierarquia:

`Região → UF → Município`

A estrutura foi validada no Tableau por meio de drill-down entre os três níveis.

O contexto técnico utilizado para geocodificação permanece separado da hierarquia analítica:

`País → Estado → Município`

Dessa forma, País e Estado auxiliam o mecanismo de mapas, enquanto Região, UF e Município representam a navegação analítica utilizada nos dashboards.

### 9.2 Hierarquia Estrutura Administrativa

Foi criada a hierarquia:

`Rede → Dependência Administrativa`

O drill-down foi validado com a seguinte estrutura:

```text
Pública
├── Federal
├── Estadual
└── Municipal

Privada
└── Privada
```

### 9.3 Indicadores de infraestrutura

Foram criados campos calculados para os indicadores de infraestrutura considerando somente escolas em atividade.

O padrão utilizado foi:

```text
IF [Escola Ativa] = 1 THEN
    [Indicador]
END
```

Foram implementados campos para:

- Internet;
- Biblioteca;
- Sala de Leitura;
- Laboratório de Ciências;
- Laboratório de Informática;
- Quadra de Esportes;
- Banheiro PNE;
- Água Potável;
- Esgoto em Rede Pública;
- Energia em Rede Pública.

Os percentuais são calculados utilizando a média dos indicadores binários:

`AVG([Indicador - Escola Ativa])`

Essa abordagem preserva:

- `1` como presença do recurso;
- `0` como ausência do recurso;
- `NULL` fora do denominador.

### 9.4 Acessibilidade

Como o campo original `IN_ACESSIBILIDADE_INEXISTENTE` possui interpretação inversa, foi criado o campo positivo:

`Acessibilidade - Escola Ativa`

utilizando a lógica:

```text
IF [Escola Ativa] = 1 THEN
    IF ISNULL([Acessibilidade Inexistente]) THEN
        NULL
    ELSE
        1 - [Acessibilidade Inexistente]
    END
END
```

O resultado passa a ser interpretado como:

- `1` = possui algum recurso de acessibilidade;
- `0` = não possui recurso de acessibilidade;
- `NULL` = informação não disponível.

### 9.5 Medidas de contagem

Também foram criados os campos calculados:

**Escolas Distintas**

`COUNTD([Código da Escola])`

**Registros Escola × Ano**

`COUNTD([ID Escola × Ano])`

**Escolas Ativas Distintas**

```text
COUNTD(
    IF [Escola Ativa] = 1 THEN
        [Código da Escola]
    END
)
```

Essas medidas permitem diferenciar escolas únicas de observações históricas Escola × Ano.

### 9.6 Validação no Tableau Cloud

Os cálculos foram testados diretamente no Tableau Cloud utilizando o ano de 2025.

Foram confirmados os KPIs:

- Matrículas: `46.018.380`;
- Docentes: `2.992.045`;
- Escolas Ativas: `180.540`;
- Salas Utilizadas: `1.646.884`.

Também foram confirmadas as contagens:

- Escolas Distintas: `214.192`;
- Registros Escola × Ano: `214.192`;
- Escolas Ativas Distintas: `180.540`.

Indicadores de infraestrutura testados:

- Internet: `94,58%`;
- Acessibilidade: `78,51%`.

As hierarquias Geografia e Estrutura Administrativa também foram validadas por meio de drill-down.

Com isso, as hierarquias e os principais campos calculados estão prontos para utilização nos dashboards.