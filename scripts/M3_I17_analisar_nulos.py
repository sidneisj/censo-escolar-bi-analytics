import pandas as pd
from pathlib import Path

DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
DATA_EXPLORACAO = Path(__file__).resolve().parent.parent / "documentation" / "exploracao"

DATA_EXPLORACAO.mkdir(parents=True, exist_ok=True)

arquivos = [
    "Tabela_Escola_2025_V2.csv",
    "Tabela_Matricula_2025_V2.csv",
    "Tabela_Docente_2025_V2.csv"
]

for arquivo in arquivos:

    caminho = DATA_RAW / arquivo

    print("=" * 80)
    print(f"ARQUIVO: {arquivo}")
    print("=" * 80)

    df = pd.read_csv(
        caminho,
        sep=";",
        encoding="latin1",
        low_memory=False
    )

    total_registros = len(df)

    resultado = []

    for coluna in df.columns:

        nulos = df[coluna].isna().sum()
        preenchidos = total_registros - nulos
        percentual_nulos = (nulos / total_registros) * 100

        resultado.append({
            "coluna": coluna,
            "registros_total": total_registros,
            "registros_nulos": nulos,
            "registros_preenchidos": preenchidos,
            "percentual_nulos": round(percentual_nulos, 2)
        })

    df_nulos = pd.DataFrame(resultado)

    # Ordenar pelas colunas com maior quantidade de nulos
    df_nulos = df_nulos.sort_values(
        by="registros_nulos",
        ascending=False
    )

    nome_saida = arquivo.replace(
        ".csv",
        "_nulos.csv"
    )

    caminho_saida = DATA_EXPLORACAO / nome_saida

    df_nulos.to_csv(
        caminho_saida,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Total de registros: {total_registros:,}")
    print(f"Colunas com algum valor nulo: {(df_nulos['registros_nulos'] > 0).sum():,}")
    print(f"Colunas sem valores nulos: {(df_nulos['registros_nulos'] == 0).sum():,}")

    print("\n10 colunas com maior quantidade de nulos:")
    print(
        df_nulos[
            ["coluna", "registros_nulos", "percentual_nulos"]
        ].head(10).to_string(index=False)
    )

    print(f"\nResultado salvo em: {caminho_saida}")
    print()

print("=" * 80)
print("Análise de valores nulos concluída.")
print("=" * 80)