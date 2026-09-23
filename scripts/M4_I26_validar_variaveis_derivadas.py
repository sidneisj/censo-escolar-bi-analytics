import pandas as pd
from pathlib import Path


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
# Valida as variáveis derivadas criadas na issue #26.
#
# O objetivo é confirmar:
#
# - ausência de valores inesperados;
# - ausência de valores nulos nas derivações;
# - coerência entre códigos oficiais e descrições;
# - distribuição das novas categorias;
# - consistência do indicador FL_ESCOLA_ATIVA.


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

ARQUIVO = PROCESSED_DIR / "escola_2025_derivada.csv"


# =============================================================================
# LEITURA
# =============================================================================

df = pd.read_csv(
    ARQUIVO,
    encoding="utf-8-sig",
    dtype={
        "CO_ENTIDADE": "string",
        "ID_ANO_ENTIDADE": "string"
    },
    low_memory=False
)


print("=" * 80)
print("VALIDAÇÃO DAS VARIÁVEIS DERIVADAS")
print("=" * 80)


# =============================================================================
# VARIÁVEIS A VALIDAR
# =============================================================================

variaveis = [
    "DS_DEPENDENCIA",
    "DS_REDE",
    "DS_LOCALIZACAO",
    "DS_SITUACAO_FUNCIONAMENTO",
    "FL_ESCOLA_ATIVA",
]


# =============================================================================
# NULOS
# =============================================================================

print("\n--- Valores nulos ---")

total_nulos = 0

for coluna in variaveis:

    quantidade = df[coluna].isna().sum()

    total_nulos += quantidade

    print(
        f"{coluna:<35} "
        f"{quantidade:>8,}"
    )


# =============================================================================
# DISTRIBUIÇÕES
# =============================================================================

print("\n--- DS_DEPENDENCIA ---")

print(
    df["DS_DEPENDENCIA"]
    .value_counts(dropna=False)
    .to_string()
)


print("\n--- DS_REDE ---")

print(
    df["DS_REDE"]
    .value_counts(dropna=False)
    .to_string()
)


print("\n--- DS_LOCALIZACAO ---")

print(
    df["DS_LOCALIZACAO"]
    .value_counts(dropna=False)
    .to_string()
)


print("\n--- DS_SITUACAO_FUNCIONAMENTO ---")

print(
    df["DS_SITUACAO_FUNCIONAMENTO"]
    .value_counts(dropna=False)
    .to_string()
)


print("\n--- FL_ESCOLA_ATIVA ---")

print(
    df["FL_ESCOLA_ATIVA"]
    .value_counts(dropna=False)
    .sort_index()
    .to_string()
)


# =============================================================================
# VALIDAÇÃO PÚBLICA / PRIVADA
# =============================================================================
# TP_DEPENDENCIA:
#
# 1 Federal
# 2 Estadual
# 3 Municipal
# 4 Privada
#
# Portanto:
#
# 1, 2 e 3 devem resultar em "Pública".
# 4 deve resultar em "Privada".


rede_esperada = df["TP_DEPENDENCIA"].map({
    1: "Pública",
    2: "Pública",
    3: "Pública",
    4: "Privada"
})


inconsistencias_rede = (
    rede_esperada != df["DS_REDE"]
).sum()


# =============================================================================
# VALIDAÇÃO DO INDICADOR DE ESCOLA ATIVA
# =============================================================================
# FL_ESCOLA_ATIVA deve ser 1 somente quando
# TP_SITUACAO_FUNCIONAMENTO == 1.

ativa_esperada = (
    df["TP_SITUACAO_FUNCIONAMENTO"] == 1
).astype(int)

inconsistencias_ativa = (
    ativa_esperada != df["FL_ESCOLA_ATIVA"]
).sum()


# =============================================================================
# CHAVE DERIVADA
# =============================================================================

nulos_id = df["ID_ANO_ENTIDADE"].isna().sum()
duplicados_id = df["ID_ANO_ENTIDADE"].duplicated().sum()


# =============================================================================
# RESUMO
# =============================================================================

print("\n" + "=" * 80)
print("RESUMO DA VALIDAÇÃO")
print("=" * 80)

print(f"Nulos nas variáveis derivadas:       {total_nulos:,}")
print(f"Inconsistências em DS_REDE:          {inconsistencias_rede:,}")
print(f"Inconsistências em FL_ESCOLA_ATIVA:  {inconsistencias_ativa:,}")
print(f"ID_ANO_ENTIDADE nulo:                {nulos_id:,}")
print(f"ID_ANO_ENTIDADE duplicado:           {duplicados_id:,}")


if (
    total_nulos == 0
    and inconsistencias_rede == 0
    and inconsistencias_ativa == 0
    and nulos_id == 0
    and duplicados_id == 0
):

    print("\nStatus: OK")

else:

    print("\nStatus: REVISAR")


print("\nValidação concluída.")
