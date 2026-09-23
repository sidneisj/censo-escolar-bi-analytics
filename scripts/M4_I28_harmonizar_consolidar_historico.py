import pandas as pd
from pathlib import Path


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
# Este script harmoniza e consolida os dados do Censo Escolar de 2019 a 2025.
#
# Estrutura de origem:
#
# 2019 a 2024:
#     um único arquivo microdados_ed_basica_XXXX.csv por ano.
#
# 2025:
#     informações distribuídas entre Escola, Matrícula e Docente.
#
# Estrutura final:
#
#     uma linha por Escola × Ano
#
# O processo:
#
# 1. seleciona apenas as variáveis utilizadas pelo projeto;
# 2. padroniza tipos e códigos;
# 3. harmoniza diferenças históricas identificadas na issue #28;
# 4. cria as mesmas variáveis derivadas em todos os anos;
# 5. reconstrói 2025 no mesmo grão dos anos anteriores;
# 6. concatena 2019 a 2025;
# 7. valida chaves, estrutura e quantidade de registros;
# 8. gera a base histórica consolidada.


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
EXPLORACAO_DIR = BASE_DIR / "documentation" / "exploracao"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
EXPLORACAO_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# ARQUIVOS 2019 A 2024
# =============================================================================

ARQUIVOS_HISTORICOS = {
    2019: RAW_DIR / "microdados_ed_basica_2019.csv",
    2020: RAW_DIR / "microdados_ed_basica_2020.csv",
    2021: RAW_DIR / "microdados_ed_basica_2021.csv",
    2022: RAW_DIR / "microdados_ed_basica_2022.csv",
    2023: RAW_DIR / "microdados_ed_basica_2023.csv",
    2024: RAW_DIR / "microdados_ed_basica_2024.csv",
}


# =============================================================================
# BASES 2025 JÁ TRATADAS NAS ISSUES ANTERIORES
# =============================================================================
# Utilizamos as bases resultantes das issues #24 e #26.
#
# Isso garante que:
#
# - o problema geográfico identificado em 2025 já esteja corrigido;
# - os valores ausentes estejam tratados segundo as regras definidas;
# - as variáveis derivadas de Escola já tenham sido validadas.

ARQUIVO_ESCOLA_2025 = (
    PROCESSED_DIR / "escola_2025_derivada.csv"
)

ARQUIVO_MATRICULA_2025 = (
    PROCESSED_DIR / "matricula_2025_derivada.csv"
)

ARQUIVO_DOCENTE_2025 = (
    PROCESSED_DIR / "docente_2025_derivada.csv"
)


# =============================================================================
# ARQUIVO FINAL
# =============================================================================

ARQUIVO_FINAL = (
    PROCESSED_DIR /
    "censo_escolar_2019_2025_consolidado.csv"
)


# =============================================================================
# VARIÁVEIS OFICIAIS UTILIZADAS
# =============================================================================

VARIAVEIS_OFICIAIS = [
    "NU_ANO_CENSO",
    "CO_ENTIDADE",
    "NO_ENTIDADE",

    "CO_REGIAO",
    "NO_REGIAO",

    "CO_UF",
    "SG_UF",
    "NO_UF",

    "CO_MUNICIPIO",
    "NO_MUNICIPIO",

    "TP_DEPENDENCIA",
    "TP_LOCALIZACAO",
    "TP_SITUACAO_FUNCIONAMENTO",

    "IN_INTERNET",
    "IN_BIBLIOTECA",
    "IN_SALA_LEITURA",
    "IN_LABORATORIO_CIENCIAS",
    "IN_LABORATORIO_INFORMATICA",
    "IN_QUADRA_ESPORTES",
    "IN_BANHEIRO_PNE",
    "IN_ACESSIBILIDADE_INEXISTENTE",
    "IN_AGUA_POTAVEL",
    "IN_ESGOTO_REDE_PUBLICA",
    "IN_ENERGIA_REDE_PUBLICA",

    "QT_SALAS_UTILIZADAS",

    "QT_MAT_BAS",
    "QT_DOC_BAS",
]


# =============================================================================
# VARIÁVEIS DERIVADAS
# =============================================================================

VARIAVEIS_DERIVADAS = [
    "ID_ANO_ENTIDADE",
    "DS_DEPENDENCIA",
    "DS_REDE",
    "DS_LOCALIZACAO",
    "DS_SITUACAO_FUNCIONAMENTO",
    "FL_ESCOLA_ATIVA",
]


COLUNAS_FINAIS = (
    VARIAVEIS_OFICIAIS
    + VARIAVEIS_DERIVADAS
)


# =============================================================================
# MAPEAMENTOS
# =============================================================================

MAPA_DEPENDENCIA = {
    1: "Federal",
    2: "Estadual",
    3: "Municipal",
    4: "Privada",
}


MAPA_REDE = {
    1: "Pública",
    2: "Pública",
    3: "Pública",
    4: "Privada",
}


MAPA_LOCALIZACAO = {
    1: "Urbana",
    2: "Rural",
}


MAPA_SITUACAO = {
    1: "Em Atividade",
    2: "Paralisada",
    3: "Extinta (ano do Censo)",
    4: "Extinta em Anos Anteriores",
}


# =============================================================================
# VARIÁVEIS DE INFRAESTRUTURA
# =============================================================================

COLUNAS_IN = [
    "IN_INTERNET",
    "IN_BIBLIOTECA",
    "IN_SALA_LEITURA",
    "IN_LABORATORIO_CIENCIAS",
    "IN_LABORATORIO_INFORMATICA",
    "IN_QUADRA_ESPORTES",
    "IN_BANHEIRO_PNE",
    "IN_ACESSIBILIDADE_INEXISTENTE",
    "IN_AGUA_POTAVEL",
    "IN_ESGOTO_REDE_PUBLICA",
    "IN_ENERGIA_REDE_PUBLICA",
]


COLUNAS_QT = [
    "QT_SALAS_UTILIZADAS",
    "QT_MAT_BAS",
    "QT_DOC_BAS",
]


# =============================================================================
# RELATÓRIO DE HARMONIZAÇÃO
# =============================================================================

harmonizacoes = []
resumo_anos = []


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def normalizar_codigo(serie, largura):
    """
    Converte identificadores numéricos para texto e preserva a largura
    esperada do código.
    """

    valores = pd.to_numeric(
        serie,
        errors="coerce"
    ).astype("Int64")

    return (
        valores
        .astype("string")
        .str.zfill(largura)
    )


def validar_mapeamento(df, coluna, mapa):
    """
    Interrompe o processo caso apareça um código categórico que não esteja
    previsto no dicionário utilizado pelo projeto.
    """

    encontrados = set(
        pd.to_numeric(
            df[coluna],
            errors="coerce"
        )
        .dropna()
        .astype(int)
        .unique()
    )

    desconhecidos = encontrados - set(mapa.keys())

    if desconhecidos:

        raise ValueError(
            f"Códigos inesperados em {coluna}: "
            f"{sorted(desconhecidos)}"
        )


# =============================================================================
# PADRONIZAÇÃO DA ESTRUTURA
# =============================================================================

def padronizar_base(df):
    """
    Aplica a mesma estrutura de tipos utilizada no ETL de 2025.
    """

    df = df.copy()


    # -------------------------------------------------------------------------
    # Ano
    # -------------------------------------------------------------------------

    df["NU_ANO_CENSO"] = pd.to_numeric(
        df["NU_ANO_CENSO"],
        errors="coerce"
    ).astype("Int64")


    # -------------------------------------------------------------------------
    # Identificadores
    # -------------------------------------------------------------------------

    df["CO_ENTIDADE"] = normalizar_codigo(
        df["CO_ENTIDADE"],
        8
    )

    df["CO_REGIAO"] = normalizar_codigo(
        df["CO_REGIAO"],
        1
    )

    df["CO_UF"] = normalizar_codigo(
        df["CO_UF"],
        2
    )

    df["CO_MUNICIPIO"] = normalizar_codigo(
        df["CO_MUNICIPIO"],
        7
    )


    # -------------------------------------------------------------------------
    # Textos
    # -------------------------------------------------------------------------

    colunas_texto = [
        "NO_ENTIDADE",
        "NO_REGIAO",
        "SG_UF",
        "NO_UF",
        "NO_MUNICIPIO",
    ]

    for coluna in colunas_texto:

        df[coluna] = (
            df[coluna]
            .astype("string")
            .str.strip()
        )


    # -------------------------------------------------------------------------
    # Categorias
    # -------------------------------------------------------------------------

    colunas_categoricas = [
        "TP_DEPENDENCIA",
        "TP_LOCALIZACAO",
        "TP_SITUACAO_FUNCIONAMENTO",
    ] + COLUNAS_IN


    for coluna in colunas_categoricas:

        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        ).astype("Int64")


    # -------------------------------------------------------------------------
    # Quantidades
    # -------------------------------------------------------------------------

    for coluna in COLUNAS_QT:

        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        ).astype("Int64")


    return df


# =============================================================================
# HARMONIZAÇÃO 2019 A 2021
# =============================================================================

def harmonizar_zeros_estruturais(df, ano):
    """
    Harmoniza a mudança de representação identificada entre 2019-2021
    e 2022-2025.

    Evidência encontrada na análise histórica:

    2019-2021:
        escolas com situação 2 ou 3 apresentam zero em:
        - QT_MAT_BAS
        - QT_DOC_BAS
        - QT_SALAS_UTILIZADAS

    2022-2025:
        os mesmos casos são representados como valor ausente.

    Para tornar a série comparável, os zeros estruturais de escolas
    paralisadas ou extintas em 2019-2021 são convertidos para NA.

    Zeros de escolas em atividade NÃO são alterados.
    """

    if ano not in [2019, 2020, 2021]:
        return df


    situacao_inativa = (
        df["TP_SITUACAO_FUNCIONAMENTO"]
        .isin([2, 3])
    )


    for coluna in COLUNAS_QT:

        mascara = (
            situacao_inativa
            & (df[coluna] == 0)
        )

        quantidade = mascara.sum()

        df.loc[
            mascara,
            coluna
        ] = pd.NA


        harmonizacoes.append({
            "ano": ano,
            "variavel": coluna,
            "regra": (
                "Zero convertido para NA em escolas "
                "com TP_SITUACAO_FUNCIONAMENTO 2 ou 3"
            ),
            "registros_afetados": quantidade,
        })


    return df


# =============================================================================
# CRIAÇÃO DAS VARIÁVEIS DERIVADAS
# =============================================================================

def criar_variaveis_derivadas(df):
    """
    Cria as mesmas variáveis analíticas definidas na issue #26.
    """

    validar_mapeamento(
        df,
        "TP_DEPENDENCIA",
        MAPA_DEPENDENCIA
    )

    validar_mapeamento(
        df,
        "TP_LOCALIZACAO",
        MAPA_LOCALIZACAO
    )

    validar_mapeamento(
        df,
        "TP_SITUACAO_FUNCIONAMENTO",
        MAPA_SITUACAO
    )


    # -------------------------------------------------------------------------
    # Chave histórica
    # -------------------------------------------------------------------------

    df["ID_ANO_ENTIDADE"] = (
        df["NU_ANO_CENSO"]
        .astype("string")
        + "_"
        + df["CO_ENTIDADE"]
        .astype("string")
    )


    # -------------------------------------------------------------------------
    # Dependência administrativa
    # -------------------------------------------------------------------------

    df["DS_DEPENDENCIA"] = (
        df["TP_DEPENDENCIA"]
        .map(MAPA_DEPENDENCIA)
        .astype("string")
    )


    # -------------------------------------------------------------------------
    # Rede pública / privada
    # -------------------------------------------------------------------------

    df["DS_REDE"] = (
        df["TP_DEPENDENCIA"]
        .map(MAPA_REDE)
        .astype("string")
    )


    # -------------------------------------------------------------------------
    # Localização
    # -------------------------------------------------------------------------

    df["DS_LOCALIZACAO"] = (
        df["TP_LOCALIZACAO"]
        .map(MAPA_LOCALIZACAO)
        .astype("string")
    )


    # -------------------------------------------------------------------------
    # Situação de funcionamento
    # -------------------------------------------------------------------------

    df["DS_SITUACAO_FUNCIONAMENTO"] = (
        df["TP_SITUACAO_FUNCIONAMENTO"]
        .map(MAPA_SITUACAO)
        .astype("string")
    )


    # -------------------------------------------------------------------------
    # Escola ativa
    # -------------------------------------------------------------------------

    df["FL_ESCOLA_ATIVA"] = (
        df["TP_SITUACAO_FUNCIONAMENTO"] == 1
    ).astype("Int64")


    return df


# =============================================================================
# VALIDAÇÃO DE CADA ANO
# =============================================================================

def validar_ano(df, ano):
    """
    Valida a base harmonizada antes da consolidação.
    """

    anos = (
        df["NU_ANO_CENSO"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    if sorted(anos) != [ano]:

        raise ValueError(
            f"Ano inesperado encontrado na base {ano}: {anos}"
        )


    chaves_nulas = (
        df[
            [
                "NU_ANO_CENSO",
                "CO_ENTIDADE",
                "ID_ANO_ENTIDADE",
            ]
        ]
        .isna()
        .any(axis=1)
        .sum()
    )


    duplicados = (
        df["ID_ANO_ENTIDADE"]
        .duplicated()
        .sum()
    )


    if chaves_nulas > 0:

        raise ValueError(
            f"{ano}: foram encontradas chaves nulas."
        )


    if duplicados > 0:

        raise ValueError(
            f"{ano}: foram encontradas chaves duplicadas."
        )


    resumo_anos.append({
        "ano": ano,
        "registros": len(df),
        "entidades_unicas": df["CO_ENTIDADE"].nunique(),
        "escolas_ativas": int(
            df["FL_ESCOLA_ATIVA"].sum()
        ),
        "nulos_qt_mat_bas": int(
            df["QT_MAT_BAS"].isna().sum()
        ),
        "nulos_qt_doc_bas": int(
            df["QT_DOC_BAS"].isna().sum()
        ),
        "nulos_qt_salas_utilizadas": int(
            df["QT_SALAS_UTILIZADAS"].isna().sum()
        ),
    })


# =============================================================================
# PROCESSAMENTO 2019 A 2024
# =============================================================================

print("=" * 80)
print("HARMONIZAÇÃO E CONSOLIDAÇÃO HISTÓRICA")
print("=" * 80)


bases_anuais = []


for ano, arquivo in ARQUIVOS_HISTORICOS.items():

    print(f"\nProcessando {ano}...")


    # -------------------------------------------------------------------------
    # Leitura apenas das colunas necessárias
    # -------------------------------------------------------------------------

    df = pd.read_csv(
        arquivo,
        sep=";",
        encoding="latin-1",
        usecols=VARIAVEIS_OFICIAIS,
        low_memory=False
    )


    # -------------------------------------------------------------------------
    # Padronização
    # -------------------------------------------------------------------------

    df = padronizar_base(df)


    # -------------------------------------------------------------------------
    # Harmonização histórica
    # -------------------------------------------------------------------------

    df = harmonizar_zeros_estruturais(
        df,
        ano
    )


    # -------------------------------------------------------------------------
    # Variáveis derivadas
    # -------------------------------------------------------------------------

    df = criar_variaveis_derivadas(df)


    # -------------------------------------------------------------------------
    # Ordenação padronizada das colunas
    # -------------------------------------------------------------------------

    df = df[COLUNAS_FINAIS]


    # -------------------------------------------------------------------------
    # Validação
    # -------------------------------------------------------------------------

    validar_ano(
        df,
        ano
    )


    bases_anuais.append(df)


    print(
        f"{len(df):,} registros | "
        f"{len(df.columns)} colunas | OK"
    )


# =============================================================================
# PROCESSAMENTO 2025
# =============================================================================

print("\nProcessando 2025...")


# -----------------------------------------------------------------------------
# Escola
# -----------------------------------------------------------------------------

df_escola_2025 = pd.read_csv(
    ARQUIVO_ESCOLA_2025,
    encoding="utf-8-sig",
    dtype={
        "CO_ENTIDADE": "string",
        "CO_REGIAO": "string",
        "CO_UF": "string",
        "CO_MUNICIPIO": "string",
        "ID_ANO_ENTIDADE": "string",
    },
    low_memory=False
)


# -----------------------------------------------------------------------------
# Matrícula
# -----------------------------------------------------------------------------

df_matricula_2025 = pd.read_csv(
    ARQUIVO_MATRICULA_2025,
    encoding="utf-8-sig",
    dtype={
        "CO_ENTIDADE": "string"
    },
    usecols=[
        "NU_ANO_CENSO",
        "CO_ENTIDADE",
        "QT_MAT_BAS",
    ],
    low_memory=False
)


# -----------------------------------------------------------------------------
# Docente
# -----------------------------------------------------------------------------

df_docente_2025 = pd.read_csv(
    ARQUIVO_DOCENTE_2025,
    encoding="utf-8-sig",
    dtype={
        "CO_ENTIDADE": "string"
    },
    usecols=[
        "NU_ANO_CENSO",
        "CO_ENTIDADE",
        "QT_DOC_BAS",
    ],
    low_memory=False
)


# =============================================================================
# MERGE 2025
# =============================================================================
# Escola representa o conjunto completo de entidades.
#
# Matrícula e Docente são incorporadas através de LEFT JOIN.

df_2025 = df_escola_2025.merge(
    df_matricula_2025,
    on=[
        "NU_ANO_CENSO",
        "CO_ENTIDADE"
    ],
    how="left",
    validate="one_to_one"
)


df_2025 = df_2025.merge(
    df_docente_2025,
    on=[
        "NU_ANO_CENSO",
        "CO_ENTIDADE"
    ],
    how="left",
    validate="one_to_one"
)


# =============================================================================
# PADRONIZAÇÃO FINAL DE 2025
# =============================================================================
# A estrutura final deve ser exatamente igual à utilizada nos anos anteriores.

df_2025 = df_2025[
    COLUNAS_FINAIS
]


validar_ano(
    df_2025,
    2025
)


bases_anuais.append(
    df_2025
)


print(
    f"{len(df_2025):,} registros | "
    f"{len(df_2025.columns)} colunas | OK"
)


# =============================================================================
# CONSOLIDAÇÃO
# =============================================================================

print("\nConsolidando 2019 a 2025...")


df_consolidado = pd.concat(
    bases_anuais,
    ignore_index=True
)


# Ordena cronologicamente e por entidade.

df_consolidado = df_consolidado.sort_values(
    [
        "NU_ANO_CENSO",
        "CO_ENTIDADE",
    ]
).reset_index(drop=True)


# =============================================================================
# VALIDAÇÕES DA BASE CONSOLIDADA
# =============================================================================

print("\n--- Validação consolidada ---")


# -----------------------------------------------------------------------------
# Estrutura
# -----------------------------------------------------------------------------

if list(df_consolidado.columns) != COLUNAS_FINAIS:

    raise ValueError(
        "A estrutura da base consolidada não corresponde "
        "à estrutura esperada."
    )


# -----------------------------------------------------------------------------
# Chaves
# -----------------------------------------------------------------------------

chaves_nulas = (
    df_consolidado[
        [
            "NU_ANO_CENSO",
            "CO_ENTIDADE",
            "ID_ANO_ENTIDADE",
        ]
    ]
    .isna()
    .any(axis=1)
    .sum()
)


duplicados = (
    df_consolidado["ID_ANO_ENTIDADE"]
    .duplicated()
    .sum()
)


# -----------------------------------------------------------------------------
# Anos
# -----------------------------------------------------------------------------

anos_encontrados = sorted(
    df_consolidado["NU_ANO_CENSO"]
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)


anos_esperados = list(
    range(2019, 2026)
)


if chaves_nulas > 0:

    raise ValueError(
        "Foram encontradas chaves nulas na base consolidada."
    )


if duplicados > 0:

    raise ValueError(
        "Foram encontradas chaves duplicadas na base consolidada."
    )


if anos_encontrados != anos_esperados:

    raise ValueError(
        f"Período histórico incorreto: {anos_encontrados}"
    )


# =============================================================================
# GERAÇÃO DA BASE CONSOLIDADA
# =============================================================================

df_consolidado.to_csv(
    ARQUIVO_FINAL,
    index=False,
    encoding="utf-8-sig"
)


# =============================================================================
# RELATÓRIO DE HARMONIZAÇÃO
# =============================================================================

df_harmonizacoes = pd.DataFrame(
    harmonizacoes
)

ARQUIVO_HARMONIZACOES = (
    EXPLORACAO_DIR /
    "harmonizacoes_historicas_2019_2025.csv"
)

df_harmonizacoes.to_csv(
    ARQUIVO_HARMONIZACOES,
    index=False,
    encoding="utf-8-sig"
)


# =============================================================================
# RESUMO POR ANO
# =============================================================================

df_resumo = pd.DataFrame(
    resumo_anos
)

ARQUIVO_RESUMO = (
    EXPLORACAO_DIR /
    "resumo_consolidacao_2019_2025.csv"
)

df_resumo.to_csv(
    ARQUIVO_RESUMO,
    index=False,
    encoding="utf-8-sig"
)


# =============================================================================
# RESULTADO
# =============================================================================

print(
    f"Registros consolidados: "
    f"{len(df_consolidado):,}"
)

print(
    f"Colunas:                "
    f"{len(df_consolidado.columns)}"
)

print(
    f"Chaves nulas:           "
    f"{chaves_nulas:,}"
)

print(
    f"Chaves duplicadas:      "
    f"{duplicados:,}"
)

print(
    f"Anos:                   "
    f"{anos_encontrados}"
)


print("\n--- Resumo por ano ---")

print(
    df_resumo.to_string(
        index=False
    )
)


print("\n--- Harmonizações realizadas ---")

if df_harmonizacoes.empty:

    print(
        "Nenhuma harmonização registrada."
    )

else:

    print(
        df_harmonizacoes.to_string(
            index=False
        )
    )


print("\nArquivos gerados:")

print(ARQUIVO_FINAL)
print(ARQUIVO_HARMONIZACOES)
print(ARQUIVO_RESUMO)


print("\n" + "=" * 80)
print("Harmonização e consolidação concluídas.")
print("=" * 80)