import pandas as pd
from pathlib import Path


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
# Este script valida a granularidade das bases históricas antes da consolidação.
#
# Objetivos:
#
# - confirmar que existe apenas um registro por escola e ano;
# - validar NU_ANO_CENSO e CO_ENTIDADE;
# - verificar duplicidades;
# - comparar a estrutura de 2019-2024 com a estrutura reconstruída de 2025;
# - analisar valores ausentes nos principais indicadores;
# - verificar a estabilidade das principais categorias oficiais.
#
# Nenhuma transformação definitiva é realizada nesta etapa.


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
EXPLORACAO_DIR = BASE_DIR / "documentation" / "exploracao"

EXPLORACAO_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# ARQUIVOS HISTÓRICOS
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
# ARQUIVOS 2025
# =============================================================================

ARQUIVO_ESCOLA_2025 = (
    RAW_DIR / "Tabela_Escola_2025_V2.csv"
)

ARQUIVO_MATRICULA_2025 = (
    RAW_DIR / "Tabela_Matricula_2025_V2.csv"
)

ARQUIVO_DOCENTE_2025 = (
    RAW_DIR / "Tabela_Docente_2025_V2.csv"
)


# =============================================================================
# VARIÁVEIS UTILIZADAS
# =============================================================================

VARIAVEIS_ESCOLA = [
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
]


VARIAVEIS_INDICADORES = [
    "QT_MAT_BAS",
    "QT_DOC_BAS",
]


VARIAVEIS_HISTORICAS = (
    VARIAVEIS_ESCOLA
    + VARIAVEIS_INDICADORES
)


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def ler_csv(caminho, colunas):
    """
    Lê apenas as colunas necessárias.

    Os arquivos históricos do INEP analisados anteriormente utilizam
    codificação Latin-1.
    """

    return pd.read_csv(
        caminho,
        sep=";",
        encoding="latin-1",
        usecols=colunas,
        low_memory=False
    )


def normalizar_chaves(df):
    """
    Padroniza as duas principais chaves utilizadas no projeto.

    NU_ANO_CENSO:
        inteiro anulável.

    CO_ENTIDADE:
        texto com 8 posições.
    """

    df["NU_ANO_CENSO"] = pd.to_numeric(
        df["NU_ANO_CENSO"],
        errors="coerce"
    ).astype("Int64")

    codigo = pd.to_numeric(
        df["CO_ENTIDADE"],
        errors="coerce"
    ).astype("Int64")

    df["CO_ENTIDADE"] = (
        codigo
        .astype("string")
        .str.zfill(8)
    )

    return df


def analisar_ano(df, ano, origem):
    """
    Produz o resumo da granularidade de um determinado ano.
    """

    total = len(df)

    entidades_unicas = (
        df["CO_ENTIDADE"]
        .nunique(dropna=True)
    )

    chaves_nulas = (
        df[
            [
                "NU_ANO_CENSO",
                "CO_ENTIDADE"
            ]
        ]
        .isna()
        .any(axis=1)
        .sum()
    )

    duplicados = (
        df.duplicated(
            subset=[
                "NU_ANO_CENSO",
                "CO_ENTIDADE"
            ],
            keep=False
        )
        .sum()
    )

    anos_encontrados = sorted(
        df["NU_ANO_CENSO"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    nulos_matricula = (
        df["QT_MAT_BAS"]
        .isna()
        .sum()
    )

    nulos_docente = (
        df["QT_DOC_BAS"]
        .isna()
        .sum()
    )

    nulos_salas = (
        df["QT_SALAS_UTILIZADAS"]
        .isna()
        .sum()
    )

    return {
        "ano": ano,
        "origem": origem,
        "registros": total,
        "entidades_unicas": entidades_unicas,
        "chaves_nulas": chaves_nulas,
        "registros_chave_duplicada": duplicados,
        "anos_encontrados": ", ".join(
            map(str, anos_encontrados)
        ),
        "nulos_qt_mat_bas": nulos_matricula,
        "nulos_qt_doc_bas": nulos_docente,
        "nulos_qt_salas_utilizadas": nulos_salas,
    }


# =============================================================================
# RESULTADOS
# =============================================================================

resultados = []
categorias = []


print("=" * 80)
print("VALIDAÇÃO DA GRANULARIDADE HISTÓRICA")
print("=" * 80)


# =============================================================================
# PROCESSAMENTO DE 2019 A 2024
# =============================================================================

for ano, arquivo in ARQUIVOS_HISTORICOS.items():

    print(f"\n{'=' * 80}")
    print(ano)
    print("=" * 80)

    df = ler_csv(
        arquivo,
        VARIAVEIS_HISTORICAS
    )

    df = normalizar_chaves(df)

    resumo = analisar_ano(
        df,
        ano,
        "arquivo_unico"
    )

    resultados.append(resumo)


    # -------------------------------------------------------------------------
    # Exibição
    # -------------------------------------------------------------------------

    print(
        f"Registros:                  "
        f"{resumo['registros']:,}"
    )

    print(
        f"Entidades únicas:           "
        f"{resumo['entidades_unicas']:,}"
    )

    print(
        f"Chaves nulas:               "
        f"{resumo['chaves_nulas']:,}"
    )

    print(
        f"Registros chave duplicada:  "
        f"{resumo['registros_chave_duplicada']:,}"
    )

    print(
        f"Ano encontrado:             "
        f"{resumo['anos_encontrados']}"
    )

    print(
        f"QT_MAT_BAS nulo:            "
        f"{resumo['nulos_qt_mat_bas']:,}"
    )

    print(
        f"QT_DOC_BAS nulo:            "
        f"{resumo['nulos_qt_doc_bas']:,}"
    )

    print(
        f"QT_SALAS_UTILIZADAS nulo:   "
        f"{resumo['nulos_qt_salas_utilizadas']:,}"
    )


    # =========================================================================
    # CATEGORIAS OFICIAIS
    # =========================================================================

    for coluna in [
        "TP_DEPENDENCIA",
        "TP_LOCALIZACAO",
        "TP_SITUACAO_FUNCIONAMENTO",
    ]:

        valores = sorted(
            pd.to_numeric(
                df[coluna],
                errors="coerce"
            )
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

        categorias.append({
            "ano": ano,
            "variavel": coluna,
            "valores_encontrados": ", ".join(
                map(str, valores)
            )
        })


# =============================================================================
# RECONSTRUÇÃO DA ESTRUTURA 2025
# =============================================================================
# Em 2025 Escola, Matrícula e Docente foram disponibilizadas separadamente.
#
# Para permitir comparação com os anos anteriores, reconstruímos aqui a mesma
# granularidade histórica:
#
# uma linha por escola / ano.
#
# A tabela Escola é usada como base e Matrícula e Docente entram através de
# LEFT JOIN.


print(f"\n{'=' * 80}")
print("2025")
print("=" * 80)


# -----------------------------------------------------------------------------
# Escola
# -----------------------------------------------------------------------------

df_escola = ler_csv(
    ARQUIVO_ESCOLA_2025,
    VARIAVEIS_ESCOLA
)

df_escola = normalizar_chaves(
    df_escola
)


# -----------------------------------------------------------------------------
# Matrícula
# -----------------------------------------------------------------------------

df_matricula = ler_csv(
    ARQUIVO_MATRICULA_2025,
    [
        "NU_ANO_CENSO",
        "CO_ENTIDADE",
        "QT_MAT_BAS",
    ]
)

df_matricula = normalizar_chaves(
    df_matricula
)


# -----------------------------------------------------------------------------
# Docente
# -----------------------------------------------------------------------------

df_docente = ler_csv(
    ARQUIVO_DOCENTE_2025,
    [
        "NU_ANO_CENSO",
        "CO_ENTIDADE",
        "QT_DOC_BAS",
    ]
)

df_docente = normalizar_chaves(
    df_docente
)


# =============================================================================
# VALIDAÇÃO PRÉ-JOIN
# =============================================================================

for nome, base in [
    ("Escola", df_escola),
    ("Matricula", df_matricula),
    ("Docente", df_docente),
]:

    duplicados = base.duplicated(
        subset=[
            "NU_ANO_CENSO",
            "CO_ENTIDADE"
        ]
    ).sum()

    if duplicados > 0:

        raise ValueError(
            f"{nome} possui {duplicados} "
            f"chave(s) duplicada(s) antes do merge."
        )


# =============================================================================
# MERGE 2025
# =============================================================================

df_2025 = df_escola.merge(
    df_matricula,
    on=[
        "NU_ANO_CENSO",
        "CO_ENTIDADE"
    ],
    how="left",
    validate="one_to_one"
)


df_2025 = df_2025.merge(
    df_docente,
    on=[
        "NU_ANO_CENSO",
        "CO_ENTIDADE"
    ],
    how="left",
    validate="one_to_one"
)


# O número de linhas deve continuar igual ao total da tabela Escola.

if len(df_2025) != len(df_escola):

    raise ValueError(
        "A quantidade de registros foi alterada "
        "durante a reconstrução de 2025."
    )


resumo_2025 = analisar_ano(
    df_2025,
    2025,
    "tabelas_separadas_reconstruidas"
)

resultados.append(
    resumo_2025
)


print(
    f"Registros:                  "
    f"{resumo_2025['registros']:,}"
)

print(
    f"Entidades únicas:           "
    f"{resumo_2025['entidades_unicas']:,}"
)

print(
    f"Chaves nulas:               "
    f"{resumo_2025['chaves_nulas']:,}"
)

print(
    f"Registros chave duplicada:  "
    f"{resumo_2025['registros_chave_duplicada']:,}"
)

print(
    f"Ano encontrado:             "
    f"{resumo_2025['anos_encontrados']}"
)

print(
    f"QT_MAT_BAS nulo:            "
    f"{resumo_2025['nulos_qt_mat_bas']:,}"
)

print(
    f"QT_DOC_BAS nulo:            "
    f"{resumo_2025['nulos_qt_doc_bas']:,}"
)

print(
    f"QT_SALAS_UTILIZADAS nulo:   "
    f"{resumo_2025['nulos_qt_salas_utilizadas']:,}"
)


# =============================================================================
# CATEGORIAS 2025
# =============================================================================

for coluna in [
    "TP_DEPENDENCIA",
    "TP_LOCALIZACAO",
    "TP_SITUACAO_FUNCIONAMENTO",
]:

    valores = sorted(
        pd.to_numeric(
            df_2025[coluna],
            errors="coerce"
        )
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    categorias.append({
        "ano": 2025,
        "variavel": coluna,
        "valores_encontrados": ", ".join(
            map(str, valores)
        )
    })


# =============================================================================
# RELATÓRIOS
# =============================================================================

df_resultados = pd.DataFrame(
    resultados
)

df_categorias = pd.DataFrame(
    categorias
)


arquivo_resumo = (
    EXPLORACAO_DIR /
    "granularidade_historica_2019_2025.csv"
)

arquivo_categorias = (
    EXPLORACAO_DIR /
    "categorias_historicas_2019_2025.csv"
)


df_resultados.to_csv(
    arquivo_resumo,
    index=False,
    encoding="utf-8-sig"
)

df_categorias.to_csv(
    arquivo_categorias,
    index=False,
    encoding="utf-8-sig"
)


# =============================================================================
# RESUMO FINAL
# =============================================================================

print("\n" + "=" * 80)
print("RESUMO HISTÓRICO")
print("=" * 80)


print(
    df_resultados[
        [
            "ano",
            "registros",
            "entidades_unicas",
            "chaves_nulas",
            "registros_chave_duplicada",
            "nulos_qt_mat_bas",
            "nulos_qt_doc_bas",
            "nulos_qt_salas_utilizadas",
        ]
    ].to_string(index=False)
)


print("\nCategorias encontradas:")

print(
    df_categorias.to_string(
        index=False
    )
)


print("\nRelatórios gerados:")

print(arquivo_resumo)
print(arquivo_categorias)

print("\nValidação concluída.")