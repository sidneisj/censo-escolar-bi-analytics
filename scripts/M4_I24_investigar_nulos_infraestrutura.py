import pandas as pd
from pathlib import Path


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
# Esta análise investiga os valores ausentes encontrados na tabela Escola
# durante a issue #24.
#
# O objetivo é verificar se a ausência das informações de infraestrutura está
# associada à situação de funcionamento das escolas ou a algum outro padrão.
#
# Nenhuma transformação é realizada neste script.

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

ARQUIVO = PROCESSED_DIR / "escola_2025_padronizada.csv"


# =============================================================================
# LEITURA
# =============================================================================

df = pd.read_csv(
    ARQUIVO,
    encoding="utf-8-sig",
    low_memory=False
)


# =============================================================================
# VARIÁVEIS DE INFRAESTRUTURA
# =============================================================================

colunas_infraestrutura = [
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


print("=" * 80)
print("INVESTIGAÇÃO DOS NULOS DE INFRAESTRUTURA")
print("=" * 80)


# =============================================================================
# IDENTIFICAÇÃO DOS REGISTROS COM INFRAESTRUTURA AUSENTE
# =============================================================================
# Como a análise anterior mostrou a mesma quantidade de nulos em todas as
# variáveis, utilizamos IN_INTERNET como referência inicial.
#
# Depois verificamos se todas as demais variáveis apresentam o mesmo padrão.

mascara_nulos = df["IN_INTERNET"].isna()

df_nulos = df[mascara_nulos].copy()
df_preenchidos = df[~mascara_nulos].copy()


print(f"\nTotal de escolas:                 {len(df):,}")
print(f"Com infraestrutura ausente:      {len(df_nulos):,}")
print(f"Com infraestrutura preenchida:   {len(df_preenchidos):,}")


# =============================================================================
# VERIFICAÇÃO DO PADRÃO ENTRE AS COLUNAS
# =============================================================================

print("\n--- Nulos por variável de infraestrutura ---")

for coluna in colunas_infraestrutura:

    quantidade = df[coluna].isna().sum()

    print(
        f"{coluna:<35} "
        f"{quantidade:>8,}"
    )


# =============================================================================
# SITUAÇÃO DE FUNCIONAMENTO
# =============================================================================
# Verifica se os registros sem infraestrutura estão concentrados em algum
# código específico de TP_SITUACAO_FUNCIONAMENTO.

print("\n--- Situação de funcionamento das escolas com infraestrutura ausente ---")

situacao_nulos = (
    df_nulos["TP_SITUACAO_FUNCIONAMENTO"]
    .value_counts(dropna=False)
    .sort_index()
)

print(situacao_nulos.to_string())


print("\n--- Situação de funcionamento das escolas com infraestrutura preenchida ---")

situacao_preenchidos = (
    df_preenchidos["TP_SITUACAO_FUNCIONAMENTO"]
    .value_counts(dropna=False)
    .sort_index()
)

print(situacao_preenchidos.to_string())


# =============================================================================
# DEPENDÊNCIA ADMINISTRATIVA
# =============================================================================
# Verifica se existe concentração dos nulos em uma determinada dependência.

print("\n--- Dependência administrativa dos registros com infraestrutura ausente ---")

dependencia = (
    df_nulos["TP_DEPENDENCIA"]
    .value_counts(dropna=False)
    .sort_index()
)

print(dependencia.to_string())


# =============================================================================
# LOCALIZAÇÃO
# =============================================================================

print("\n--- Localização dos registros com infraestrutura ausente ---")

localizacao = (
    df_nulos["TP_LOCALIZACAO"]
    .value_counts(dropna=False)
    .sort_index()
)

print(localizacao.to_string())


# =============================================================================
# REGISTRO COM INFORMAÇÕES GEOGRÁFICAS AUSENTES
# =============================================================================
# Na análise anterior foi identificado um único registro sem NO_REGIAO,
# SG_UF, NO_UF e NO_MUNICIPIO.
#
# Aqui mostramos seus principais identificadores para investigação.

colunas_geograficas = [
    "NO_REGIAO",
    "SG_UF",
    "NO_UF",
    "NO_MUNICIPIO",
]

mascara_geo = df[colunas_geograficas].isna().any(axis=1)

df_geo_nulos = df[mascara_geo][
    [
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
    ]
]

print("\n--- Registros com informações geográficas ausentes ---")

if df_geo_nulos.empty:

    print("Nenhum registro encontrado.")

else:

    print(
        df_geo_nulos.to_string(
            index=False
        )
    )


print("\n" + "=" * 80)
print("Investigação concluída.")
print("=" * 80)