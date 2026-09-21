import pandas as pd
from pathlib import Path

# Caminho da pasta com os dados brutos
DATA_RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

# Caminho onde os resultados da exploração serão armazenados
DATA_EXPLORACAO = Path(__file__).resolve().parent.parent / "documentation" / "exploracao"

# Cria a pasta caso ela ainda não exista
DATA_EXPLORACAO.mkdir(parents=True, exist_ok=True)

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

    # Leitura do arquivo
    df = pd.read_csv(
        caminho,
        sep=";",
        encoding="latin1",
        low_memory=False
    )

    print(f"Linhas: {df.shape[0]:,}")
    print(f"Colunas: {df.shape[1]:,}")

    # Criação do inventário das colunas
    inventario = []

    for numero, coluna in enumerate(df.columns, start=1):
        tipo = df[coluna].dtype
        preenchidos = df[coluna].notna().sum()
        percentual = (preenchidos / len(df)) * 100

        inventario.append({
            "ordem": numero,
            "coluna": coluna,
            "tipo": str(tipo),
            "registros_total": len(df),
            "registros_preenchidos": preenchidos,
            "percentual_preenchido": round(percentual, 2)
        })

    # Transformar o inventário em DataFrame
    df_inventario = pd.DataFrame(inventario)

    # Nome do arquivo de saída
    nome_inventario = arquivo.replace(".csv", "_inventario.csv")
    caminho_inventario = DATA_EXPLORACAO / nome_inventario

    # Salvar inventário
    df_inventario.to_csv(
        caminho_inventario,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Inventário salvo em: {caminho_inventario}")
    print()

print("=" * 80)
print("Exploração concluída.")
print("=" * 80)
