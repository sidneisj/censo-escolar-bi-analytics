import pandas as pd
from pathlib import Path

DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

arquivo = "Tabela_Escola_2025_V2.csv"
#arquivo = "Tabela_Matricula_2025_V2.csv"
#arquivo = "Tabela_Docente_2025_V2.csv"
caminho = DATA_RAW / arquivo

print("=" * 80)
print(f"ANÁLISE DE VALORES CATEGÓRICOS - {arquivo}")
print("=" * 80)

df = pd.read_csv(
    caminho,
    sep=";",
    encoding="latin1",
    low_memory=False
)

colunas = [
    coluna for coluna in df.columns
    if coluna.startswith(("TP_", "IN_"))
]

print(f"\nTotal de variáveis analisadas: {len(colunas)}")

for coluna in colunas:
    valores = df[coluna].value_counts(dropna=False)

    print("\n" + "-" * 80)
    print(f"VARIÁVEL: {coluna}")
    print("-" * 80)

    if len(valores) <= 20:
        print(valores.to_string())
    else:
        print(f"Quantidade de valores distintos: {len(valores)}")
        print("Primeiros valores:")
        print(valores.head(20).to_string())

print("\n" + "=" * 80)
print("Análise concluída.")
print("=" * 80)