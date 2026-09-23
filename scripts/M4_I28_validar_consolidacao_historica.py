import pandas as pd
from pathlib import Path


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
# Este script valida a base histórica consolidada gerada na issue #28.
#
# Objetivos:
#
# - confirmar a quantidade de registros por ano;
# - validar unicidade da chave ID_ANO_ENTIDADE;
# - comparar os principais indicadores da base consolidada com as fontes
#   originais de cada ano;
# - confirmar que a harmonização de zeros para NA em 2019-2021 não alterou
#   os totais quantitativos;
# - validar as distribuições das principais categorias;
# - confirmar o período histórico completo de 2019 a 2025.
#
# Nenhuma transformação é realizada.


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
EXPLORACAO_DIR = BASE_DIR / "documentation" / "exploracao"

EXPLORACAO_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# BASE CONSOLIDADA
# =============================================================================

ARQUIVO_CONSOLIDADO = (
    PROCESSED_DIR /
    "censo_escolar_2019_2025_consolidado.csv"
)


# =============================================================================
# FONTES HISTÓRICAS
# =============================================================================

ARQUIVOS_HISTORICOS = {
    2019: RAW_DIR / "microdados_ed_basica_2019.csv",
    2020: RAW_DIR / "microdados_ed_basica_2020.csv",
    2021: RAW_DIR / "microdados_ed_basica_2021.csv",
    2022: RAW_DIR / "microdados_ed_basica_2022.csv",
    2023: RAW_DIR / "microdados_ed_basica_2023.csv",
    2024: RAW_DIR / "microdados_ed_basica_2024.csv",
}


ARQUIVOS_2025 = {
    "Escola": RAW_DIR / "Tabela_Escola_2025_V2.csv",
    "Matricula": RAW_DIR / "Tabela_Matricula_2025_V2.csv",
    "Docente": RAW_DIR / "Tabela_Docente_2025_V2.csv",
}


# =============================================================================
# INDICADORES
# =============================================================================

INDICADORES = [
    "QT_MAT_BAS",
    "QT_DOC_BAS",
    "QT_SALAS_UTILIZADAS",
]


CATEGORIAS = [
    "TP_DEPENDENCIA",
    "TP_LOCALIZACAO",
    "TP_SITUACAO_FUNCIONAMENTO",
]


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def ler_raw(caminho, colunas):
    """
    Lê somente as colunas necessárias das fontes originais do INEP.
    """

    return pd.read_csv(
        caminho,
        sep=";",
        encoding="latin-1",
        usecols=colunas,
        low_memory=False
    )


def soma_numerica(serie):
    """
    Converte a série para numérico e retorna sua soma.

    A transformação 0 -> NA realizada em 2019-2021 não deve alterar
    o resultado da soma.
    """

    return pd.to_numeric(
        serie,
        errors="coerce"
    ).sum()


# =============================================================================
# LEITURA DA BASE CONSOLIDADA
# =============================================================================

df = pd.read_csv(
    ARQUIVO_CONSOLIDADO,
    encoding="utf-8-sig",
    dtype={
        "CO_ENTIDADE": "string",
        "ID_ANO_ENTIDADE": "string",
    },
    low_memory=False
)


print("=" * 80)
print("VALIDAÇÃO DA CONSOLIDAÇÃO HISTÓRICA")
print("=" * 80)


resultados = []


def registrar(ano, grupo, teste, esperado, observado, valido):
    """
    Registra cada teste realizado.
    """

    resultados.append({
        "ano": ano,
        "grupo": grupo,
        "teste": teste,
        "esperado": str(esperado),
        "observado": str(observado),
        "status": "OK" if valido else "REVISAR",
    })


# =============================================================================
# 1. PERÍODO HISTÓRICO
# =============================================================================

anos_encontrados = sorted(
    pd.to_numeric(
        df["NU_ANO_CENSO"],
        errors="coerce"
    )
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)

anos_esperados = list(range(2019, 2026))

periodo_ok = anos_encontrados == anos_esperados

print("\n--- Período histórico ---")
print(f"Esperado:   {anos_esperados}")
print(f"Encontrado: {anos_encontrados}")
print(f"Status:     {'OK' if periodo_ok else 'REVISAR'}")


registrar(
    "Geral",
    "Período",
    "Anos presentes",
    anos_esperados,
    anos_encontrados,
    periodo_ok
)


# =============================================================================
# 2. CHAVES
# =============================================================================

print("\n--- Chaves consolidadas ---")

chaves_nulas = (
    df[
        [
            "NU_ANO_CENSO",
            "CO_ENTIDADE",
            "ID_ANO_ENTIDADE"
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


print(f"Chaves nulas:      {chaves_nulas:,}")
print(f"Chaves duplicadas: {duplicados:,}")


registrar(
    "Geral",
    "Chaves",
    "Chaves nulas",
    0,
    chaves_nulas,
    chaves_nulas == 0
)

registrar(
    "Geral",
    "Chaves",
    "ID_ANO_ENTIDADE duplicada",
    0,
    duplicados,
    duplicados == 0
)


# =============================================================================
# 3. VALIDAÇÃO 2019 A 2024
# =============================================================================

for ano, arquivo in ARQUIVOS_HISTORICOS.items():

    print(f"\n{'=' * 80}")
    print(ano)
    print("=" * 80)

    df_ano = df[
        df["NU_ANO_CENSO"] == ano
    ]


    raw = ler_raw(
        arquivo,
        [
            "CO_ENTIDADE",
            *INDICADORES,
            *CATEGORIAS,
        ]
    )


    # -------------------------------------------------------------------------
    # Quantidade de registros
    # -------------------------------------------------------------------------

    registros_raw = len(raw)
    registros_final = len(df_ano)

    valido = registros_raw == registros_final

    print(
        f"Registros "
        f"RAW: {registros_raw:,} | "
        f"FINAL: {registros_final:,} | "
        f"{'OK' if valido else 'REVISAR'}"
    )

    registrar(
        ano,
        "Registros",
        "Quantidade de registros",
        registros_raw,
        registros_final,
        valido
    )


    # -------------------------------------------------------------------------
    # Indicadores
    # -------------------------------------------------------------------------

    for coluna in INDICADORES:

        total_raw = soma_numerica(
            raw[coluna]
        )

        total_final = soma_numerica(
            df_ano[coluna]
        )

        valido = total_raw == total_final

        print(
            f"{coluna:<25} "
            f"RAW: {total_raw:,.0f} | "
            f"FINAL: {total_final:,.0f} | "
            f"{'OK' if valido else 'REVISAR'}"
        )

        registrar(
            ano,
            "Indicadores",
            f"Total {coluna}",
            total_raw,
            total_final,
            valido
        )


    # -------------------------------------------------------------------------
    # Categorias
    # -------------------------------------------------------------------------

    for coluna in CATEGORIAS:

        distribuicao_raw = (
            pd.to_numeric(
                raw[coluna],
                errors="coerce"
            )
            .value_counts(dropna=False)
            .sort_index()
            .to_dict()
        )

        distribuicao_final = (
            pd.to_numeric(
                df_ano[coluna],
                errors="coerce"
            )
            .value_counts(dropna=False)
            .sort_index()
            .to_dict()
        )

        valido = (
            distribuicao_raw ==
            distribuicao_final
        )

        registrar(
            ano,
            "Categorias",
            f"Distribuição {coluna}",
            distribuicao_raw,
            distribuicao_final,
            valido
        )

        print(
            f"{coluna:<35} "
            f"{'OK' if valido else 'REVISAR'}"
        )


# =============================================================================
# 4. VALIDAÇÃO DE 2025
# =============================================================================

print(f"\n{'=' * 80}")
print("2025")
print("=" * 80)


df_2025 = df[
    df["NU_ANO_CENSO"] == 2025
]


# -----------------------------------------------------------------------------
# Escola
# -----------------------------------------------------------------------------

raw_escola = ler_raw(
    ARQUIVOS_2025["Escola"],
    [
        "CO_ENTIDADE",
        "QT_SALAS_UTILIZADAS",
        *CATEGORIAS,
    ]
)


# -----------------------------------------------------------------------------
# Matrícula
# -----------------------------------------------------------------------------

raw_matricula = ler_raw(
    ARQUIVOS_2025["Matricula"],
    [
        "QT_MAT_BAS"
    ]
)


# -----------------------------------------------------------------------------
# Docente
# -----------------------------------------------------------------------------

raw_docente = ler_raw(
    ARQUIVOS_2025["Docente"],
    [
        "QT_DOC_BAS"
    ]
)


# =============================================================================
# REGISTROS 2025
# =============================================================================

registros_raw = len(raw_escola)
registros_final = len(df_2025)

valido = registros_raw == registros_final


print(
    f"Registros "
    f"RAW Escola: {registros_raw:,} | "
    f"FINAL: {registros_final:,} | "
    f"{'OK' if valido else 'REVISAR'}"
)


registrar(
    2025,
    "Registros",
    "Quantidade de registros",
    registros_raw,
    registros_final,
    valido
)


# =============================================================================
# INDICADORES 2025
# =============================================================================

fontes_indicadores_2025 = {
    "QT_SALAS_UTILIZADAS":
        raw_escola["QT_SALAS_UTILIZADAS"],

    "QT_MAT_BAS":
        raw_matricula["QT_MAT_BAS"],

    "QT_DOC_BAS":
        raw_docente["QT_DOC_BAS"],
}


for coluna, serie_raw in fontes_indicadores_2025.items():

    total_raw = soma_numerica(
        serie_raw
    )

    total_final = soma_numerica(
        df_2025[coluna]
    )

    valido = total_raw == total_final

    print(
        f"{coluna:<25} "
        f"RAW: {total_raw:,.0f} | "
        f"FINAL: {total_final:,.0f} | "
        f"{'OK' if valido else 'REVISAR'}"
    )

    registrar(
        2025,
        "Indicadores",
        f"Total {coluna}",
        total_raw,
        total_final,
        valido
    )


# =============================================================================
# CATEGORIAS 2025
# =============================================================================

for coluna in CATEGORIAS:

    distribuicao_raw = (
        pd.to_numeric(
            raw_escola[coluna],
            errors="coerce"
        )
        .value_counts(dropna=False)
        .sort_index()
        .to_dict()
    )

    distribuicao_final = (
        pd.to_numeric(
            df_2025[coluna],
            errors="coerce"
        )
        .value_counts(dropna=False)
        .sort_index()
        .to_dict()
    )

    valido = (
        distribuicao_raw ==
        distribuicao_final
    )

    registrar(
        2025,
        "Categorias",
        f"Distribuição {coluna}",
        distribuicao_raw,
        distribuicao_final,
        valido
    )

    print(
        f"{coluna:<35} "
        f"{'OK' if valido else 'REVISAR'}"
    )


# =============================================================================
# 5. QUANTIDADE DE REGISTROS POR ANO
# =============================================================================

print("\n" + "=" * 80)
print("REGISTROS POR ANO")
print("=" * 80)

resumo_anos = (
    df
    .groupby("NU_ANO_CENSO")
    .agg(
        registros=("ID_ANO_ENTIDADE", "size"),
        entidades=("CO_ENTIDADE", "nunique"),
        escolas_ativas=("FL_ESCOLA_ATIVA", "sum"),
    )
    .reset_index()
)

print(
    resumo_anos.to_string(
        index=False
    )
)


# =============================================================================
# 6. RELATÓRIO FINAL
# =============================================================================

df_resultados = pd.DataFrame(
    resultados
)

ARQUIVO_RELATORIO = (
    EXPLORACAO_DIR /
    "validacao_consolidacao_2019_2025.csv"
)

df_resultados.to_csv(
    ARQUIVO_RELATORIO,
    index=False,
    encoding="utf-8-sig"
)


quantidade_ok = (
    df_resultados["status"] == "OK"
).sum()

quantidade_revisar = (
    df_resultados["status"] == "REVISAR"
).sum()


print("\n" + "=" * 80)
print("RESUMO FINAL")
print("=" * 80)

print(f"Testes OK:      {quantidade_ok}")
print(f"Testes REVISAR: {quantidade_revisar}")


if quantidade_revisar == 0:

    print("\nSTATUS FINAL: OK")

else:

    print("\nSTATUS FINAL: REVISAR")


print("\nRelatório gerado:")
print(ARQUIVO_RELATORIO)

print("\nValidação concluída.")