import pandas as pd
from pathlib import Path

DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

# Ler apenas CO_ENTIDADE das tabelas necessárias
matricula = pd.read_csv(
    DATA_RAW / "Tabela_Matricula_2025_V2.csv",
    sep=";",
    encoding="latin1",
    low_memory=False,
    usecols=["CO_ENTIDADE"]
)

docente = pd.read_csv(
    DATA_RAW / "Tabela_Docente_2025_V2.csv",
    sep=";",
    encoding="latin1",
    low_memory=False,
    usecols=["CO_ENTIDADE"]
)

escola = pd.read_csv(
    DATA_RAW / "Tabela_Escola_2025_V2.csv",
    sep=";",
    encoding="latin1",
    low_memory=False,
    usecols=["CO_ENTIDADE"]
)

# Conjuntos de entidades
entidades_matricula = set(matricula["CO_ENTIDADE"])
entidades_docente = set(docente["CO_ENTIDADE"])
entidades_escola = set(escola["CO_ENTIDADE"])

# Entidades presentes em Docente, mas ausentes em Matrícula
somente_docente = entidades_docente - entidades_matricula

print("=" * 80)
print("ENTIDADES PRESENTES SOMENTE EM DOCENTE")
print("=" * 80)

print(f"Quantidade: {len(somente_docente)}")
print()

for entidade in sorted(somente_docente):
    print(entidade)

print()
print("=" * 80)
print("VERIFICAÇÃO NA TABELA ESCOLA")
print("=" * 80)

for entidade in sorted(somente_docente):
    presente = entidade in entidades_escola
    print(f"CO_ENTIDADE {entidade}: presente em Escola = {presente}")

print()
print("=" * 80)
print("Investigação concluída.")
print("=" * 80)