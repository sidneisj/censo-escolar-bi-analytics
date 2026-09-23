import pandas as pd
from pathlib import Path

DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

arquivo = "Tabela_Escola_2025_V2.csv"

caminho = DATA_RAW / arquivo

print("=" * 80)
print(f"ANÁLISE DE VALORES QUANTITATIVOS - {arquivo}")
print("=" * 80)

df = pd.read_csv(
    caminho,
    sep=";",
    encoding="latin1",
    low_memory=False
)

# Selecionar variáveis de quantidade
colunas_quantidade = [
    coluna
    for coluna in df.columns
    if coluna.startswith("QT_")
]

print(f"\nTotal de variáveis QT_: {len(colunas_quantidade)}")

print("\n" + "=" * 80)
print("VALORES NEGATIVOS")
print("=" * 80)

encontrou_negativos = False

for coluna in colunas_quantidade:

    negativos = (df[coluna] < 0).sum()

    if negativos > 0:
        encontrou_negativos = True
        print(f"{coluna}: {negativos:,} valores negativos")

if not encontrou_negativos:
    print("Nenhum valor negativo encontrado.")

print("\n" + "=" * 80)
print("VALORES MÍNIMOS E MÁXIMOS")
print("=" * 80)

resultado = []

for coluna in colunas_quantidade:

    minimo = df[coluna].min()
    maximo = df[coluna].max()

    resultado.append({
        "coluna": coluna,
        "minimo": minimo,
        "maximo": maximo
    })

df_resultado = pd.DataFrame(resultado)

print(df_resultado.to_string(index=False))

print("\n" + "=" * 80)
print("Análise concluída.")
print("=" * 80)