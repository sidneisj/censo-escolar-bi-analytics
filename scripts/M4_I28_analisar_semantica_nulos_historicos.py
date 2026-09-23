import pandas as pd
from pathlib import Path


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
# Este script investiga a mudança no padrão de preenchimento dos indicadores
# quantitativos entre 2019 e 2025.
#
# A análise anterior mostrou:
#
# - 2019 a 2021: nenhum valor nulo nos indicadores selecionados;
# - 2022 a 2025: milhares de valores nulos.
#
# O objetivo agora é verificar se, nos anos anteriores, registros que
# posteriormente passaram a ser representados como NA eram armazenados como 0.
#
# Nenhuma transformação é realizada neste script.


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
# VARIÁVEIS ANALISADAS
# =============================================================================

INDICADORES = [
    "QT_MAT_BAS",
    "QT_DOC_BAS",
    "QT_SALAS_UTILIZADAS",
]


# =============================================================================
# LEITURA
# =============================================================================

def ler_csv(caminho, colunas):
    """
    Lê somente as colunas necessárias dos arquivos do INEP.
    """

    return pd.read_csv(
        caminho,
        sep=";",
        encoding="latin-1",
        usecols=colunas,
        low_memory=False
    )


# =============================================================================
# ANÁLISE
# =============================================================================

def analisar(df, ano):
    """
    Analisa cada indicador segundo a situação de funcionamento da escola.

    Para cada combinação são contados:

    - registros;
    - valores nulos;
    - valores iguais a zero;
    - valores maiores que zero;
    - valores negativos;
    - soma dos valores válidos.
    """

    resultados = []

    for situacao in sorted(
        df["TP_SITUACAO_FUNCIONAMENTO"]
        .dropna()
        .unique()
    ):

        dados_situacao = df[
            df["TP_SITUACAO_FUNCIONAMENTO"] == situacao
        ]

        for coluna in INDICADORES:

            serie = pd.to_numeric(
                dados_situacao[coluna],
                errors="coerce"
            )

            resultados.append({
                "ano": ano,
                "tp_situacao_funcionamento": int(situacao),
                "variavel": coluna,
                "registros": len(serie),
                "nulos": serie.isna().sum(),
                "zeros": (serie == 0).sum(),
                "positivos": (serie > 0).sum(),
                "negativos": (serie < 0).sum(),
                "soma": serie.sum(),
            })

    return resultados


# =============================================================================
# EXECUÇÃO
# =============================================================================

resultado_final = []


print("=" * 80)
print("ANÁLISE HISTÓRICA DE NULOS E ZEROS")
print("=" * 80)


# =============================================================================
# 2019 A 2024
# =============================================================================

for ano, arquivo in ARQUIVOS_HISTORICOS.items():

    df = ler_csv(
        arquivo,
        [
            "TP_SITUACAO_FUNCIONAMENTO",
            "QT_MAT_BAS",
            "QT_DOC_BAS",
            "QT_SALAS_UTILIZADAS",
        ]
    )

    resultado_final.extend(
        analisar(df, ano)
    )


# =============================================================================
# 2025
# =============================================================================
# Em 2025 os indicadores estão divididos em três arquivos.
#
# Reconstruímos uma linha por escola para manter a mesma granularidade
# utilizada nos anos anteriores.


df_escola = ler_csv(
    ARQUIVO_ESCOLA_2025,
    [
        "NU_ANO_CENSO",
        "CO_ENTIDADE",
        "TP_SITUACAO_FUNCIONAMENTO",
        "QT_SALAS_UTILIZADAS",
    ]
)


df_matricula = ler_csv(
    ARQUIVO_MATRICULA_2025,
    [
        "NU_ANO_CENSO",
        "CO_ENTIDADE",
        "QT_MAT_BAS",
    ]
)


df_docente = ler_csv(
    ARQUIVO_DOCENTE_2025,
    [
        "NU_ANO_CENSO",
        "CO_ENTIDADE",
        "QT_DOC_BAS",
    ]
)


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


resultado_final.extend(
    analisar(df_2025, 2025)
)


# =============================================================================
# RESULTADO CONSOLIDADO
# =============================================================================

df_resultado = pd.DataFrame(
    resultado_final
)


# =============================================================================
# EXIBIÇÃO
# =============================================================================

for ano in range(2019, 2026):

    print(f"\n{'=' * 80}")
    print(ano)
    print("=" * 80)

    dados_ano = df_resultado[
        df_resultado["ano"] == ano
    ]

    print(
        dados_ano[
            [
                "tp_situacao_funcionamento",
                "variavel",
                "registros",
                "nulos",
                "zeros",
                "positivos",
            ]
        ].to_string(index=False)
    )


# =============================================================================
# EXPORTAÇÃO
# =============================================================================

arquivo_saida = (
    EXPLORACAO_DIR /
    "semantica_nulos_historicos_2019_2025.csv"
)


df_resultado.to_csv(
    arquivo_saida,
    index=False,
    encoding="utf-8-sig"
)


print("\n" + "=" * 80)
print("Relatório gerado:")
print(arquivo_saida)

print("\nAnálise concluída.")
