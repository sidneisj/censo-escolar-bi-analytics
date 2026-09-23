import pandas as pd
from pathlib import Path

DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

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

    # Linhas totalmente duplicadas
    duplicados_exatos = df.duplicated(keep=False).sum()

    # Quantidade de linhas duplicadas mantendo a primeira ocorrência
    duplicados_removiveis = df.duplicated(keep="first").sum()

    # Registros únicos após remoção das duplicidades exatas
    registros_unicos = total_registros - duplicados_removiveis

    # Verificação da chave
    duplicados_chave = df["CO_ENTIDADE"].duplicated(keep=False).sum()

    print(f"Registros totais: {total_registros:,}")
    print(f"Linhas totalmente duplicadas: {duplicados_exatos:,}")
    print(f"Linhas duplicadas além da primeira ocorrência: {duplicados_removiveis:,}")
    print(f"Registros únicos após deduplicação: {registros_unicos:,}")
    print(f"Registros com CO_ENTIDADE duplicado: {duplicados_chave:,}")
    print()

print("=" * 80)
print("Verificação de duplicidades concluída.")
print("=" * 80)