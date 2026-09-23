import pandas as pd
from pathlib import Path

DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

arquivo = "Tabela_Escola_2025_V2.csv"

caminho = DATA_RAW / arquivo

print("=" * 80)
print(f"ANÁLISE DE VALORES - {arquivo}")
print("=" * 80)

# Variáveis categóricas selecionadas para análise inicial
colunas = [
    "TP_DEPENDENCIA",
    "TP_LOCALIZACAO",
    "TP_SITUACAO_FUNCIONAMENTO",
    "TP_CATEGORIA_ESCOLA_PRIVADA",
    "TP_PODER_PUBLICO_PARCERIA"
]

df = pd.read_csv(
    caminho,
    sep=";",
    encoding="latin1",
    low_memory=False,
    usecols=colunas
)

for coluna in colunas:

    print()
    print("-" * 80)
    print(f"VARIÁVEL: {coluna}")
    print("-" * 80)

    frequencias = df[coluna].value_counts(
        dropna=False
    ).sort_index()

    print(frequencias.to_string())

print()
print("=" * 80)
print("Análise inicial concluída.")
print("=" * 80)