import pandas as pd
from pathlib import Path

# Caminho da pasta com os dados brutos
DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

# Arquivos
arquivos = {
    "Escola": "Tabela_Escola_2025_V2.csv",
    "Matrícula": "Tabela_Matricula_2025_V2.csv",
    "Docente": "Tabela_Docente_2025_V2.csv"
}

# Armazena os conjuntos de CO_ENTIDADE
entidades = {}

for nome, arquivo in arquivos.items():

    caminho = DATA_RAW / arquivo

    print(f"Lendo: {arquivo}")

    df = pd.read_csv(
        caminho,
        sep=";",
        encoding="latin1",
        low_memory=False,
        usecols=["CO_ENTIDADE"]
    )

    entidades[nome] = set(df["CO_ENTIDADE"])

print()
print("=" * 80)
print("RELACIONAMENTOS ENTRE AS TABELAS")
print("=" * 80)

# Quantidade de entidades em cada tabela
for nome, conjunto in entidades.items():
    print(f"{nome}: {len(conjunto):,} entidades")

print()

# Função para comparar duas tabelas
def comparar(tabela_a, tabela_b):

    conjunto_a = entidades[tabela_a]
    conjunto_b = entidades[tabela_b]

    comuns = conjunto_a & conjunto_b
    somente_a = conjunto_a - conjunto_b
    somente_b = conjunto_b - conjunto_a

    print("-" * 80)
    print(f"{tabela_a} x {tabela_b}")
    print("-" * 80)

    print(f"Entidades em comum: {len(comuns):,}")
    print(f"Somente em {tabela_a}: {len(somente_a):,}")
    print(f"Somente em {tabela_b}: {len(somente_b):,}")


comparar("Escola", "Matrícula")
comparar("Escola", "Docente")
comparar("Matrícula", "Docente")

print()
print("=" * 80)
print("Validação de relacionamentos concluída.")
print("=" * 80)