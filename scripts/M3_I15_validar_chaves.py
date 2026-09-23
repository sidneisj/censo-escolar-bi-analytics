import pandas as pd
from pathlib import Path

# Caminho da pasta com os dados brutos
DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

# Arquivos selecionados
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

    coluna_chave = "CO_ENTIDADE"

    # Quantidade de registros
    total_registros = len(df)

    # Valores nulos
    nulos = df[coluna_chave].isna().sum()

    # Valores únicos
    unicos = df[coluna_chave].nunique()

    # Registros duplicados da chave
    duplicados = df[coluna_chave].duplicated(keep=False).sum()

    # Quantidade de chaves que aparecem mais de uma vez
    chaves_duplicadas = (
        df[coluna_chave]
        .value_counts()
        .gt(1)
        .sum()
    )

    print(f"Registros: {total_registros:,}")
    print(f"CO_ENTIDADE nulos: {nulos:,}")
    print(f"CO_ENTIDADE únicos: {unicos:,}")
    print(f"Registros com CO_ENTIDADE duplicado: {duplicados:,}")
    print(f"Chaves CO_ENTIDADE duplicadas: {chaves_duplicadas:,}")
    print()

print("=" * 80)
print("Validação de chaves concluída.")
print("=" * 80)