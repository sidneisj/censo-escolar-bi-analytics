import pandas as pd
from pathlib import Path


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
# Nesta etapa utilizamos as bases já padronizadas geradas na issue #23.
# Os arquivos brutos permanecem inalterados.

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


ARQUIVOS = {
    "Escola": PROCESSED_DIR / "escola_2025_padronizada.csv",
    "Matricula": PROCESSED_DIR / "matricula_2025_padronizada.csv",
    "Docente": PROCESSED_DIR / "docente_2025_padronizada.csv",
}


# =============================================================================
# VALORES ESPECIAIS
# =============================================================================
# Durante a etapa de Data Quality foi identificado que o INEP utiliza
# determinados códigos especiais em variáveis quantitativas.
#
# O valor 88888, por exemplo, pode representar uma marcação oficial de
# valor extremo e não deve ser interpretado como uma quantidade real.
#
# Nesta etapa apenas identificamos sua ocorrência.
# Nenhuma substituição será realizada ainda.

VALORES_ESPECIAIS = [
    88888
]


# =============================================================================
# EXECUÇÃO
# =============================================================================

print("=" * 80)
print("ANÁLISE DE VALORES AUSENTES E ESPECIAIS")
print("=" * 80)


for tabela, arquivo in ARQUIVOS.items():

    print(f"\n{'=' * 80}")
    print(tabela.upper())
    print("=" * 80)

    df = pd.read_csv(
        arquivo,
        encoding="utf-8-sig",
        low_memory=False
    )

    total_registros = len(df)

    print(f"\nRegistros: {total_registros:,}")
    print(f"Colunas:   {len(df.columns)}")


    # =========================================================================
    # VALORES AUSENTES
    # =========================================================================

    print("\n--- Valores ausentes ---")

    encontrou_nulos = False

    for coluna in df.columns:

        quantidade = df[coluna].isna().sum()

        if quantidade > 0:

            encontrou_nulos = True

            percentual = (
                quantidade / total_registros
            ) * 100

            print(
                f"{coluna:<35} "
                f"{quantidade:>8,} "
                f"({percentual:6.2f}%)"
            )

    if not encontrou_nulos:
        print("Nenhum valor ausente identificado.")


    # =========================================================================
    # VALORES ESPECIAIS
    # =========================================================================
    # A busca é realizada apenas em colunas quantitativas iniciadas por QT_.

    print("\n--- Valores especiais em variáveis quantitativas ---")

    colunas_quantitativas = [
        coluna
        for coluna in df.columns
        if coluna.startswith("QT_")
    ]

    encontrou_especial = False

    for coluna in colunas_quantitativas:

        serie_numerica = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )

        for valor in VALORES_ESPECIAIS:

            quantidade = (
                serie_numerica == valor
            ).sum()

            if quantidade > 0:

                encontrou_especial = True

                percentual = (
                    quantidade / total_registros
                ) * 100

                print(
                    f"{coluna:<35} "
                    f"valor {valor}: "
                    f"{quantidade:,} "
                    f"({percentual:.4f}%)"
                )

    if not encontrou_especial:
        print("Nenhum valor especial identificado.")


    # =========================================================================
    # VALORES DAS VARIÁVEIS CATEGÓRICAS
    # =========================================================================
    # Também mostramos os códigos encontrados nas variáveis TP_ e IN_.
    #
    # Isso ajuda a detectar códigos como 9 ou outras situações especiais que
    # eventualmente devam receber tratamento específico.

    print("\n--- Categorias observadas ---")

    colunas_categoricas = [
        coluna
        for coluna in df.columns
        if coluna.startswith(("TP_", "IN_"))
    ]

    if not colunas_categoricas:

        print("Nenhuma variável categórica nesta tabela.")

    else:

        for coluna in colunas_categoricas:

            valores = (
                df[coluna]
                .dropna()
                .unique()
                .tolist()
            )

            valores = sorted(valores)

            print(
                f"{coluna:<35} "
                f"{valores}"
            )


print("\n" + "=" * 80)
print("Análise concluída.")
print("=" * 80)