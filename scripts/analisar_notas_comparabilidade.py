import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTATION = BASE_DIR / "documentation" / "inep"
OUTPUT_DIR = BASE_DIR / "documentation" / "exploracao"

arquivos = list(DOCUMENTATION.glob("*dicion*.xlsx"))

if not arquivos:
    raise FileNotFoundError("Dicionário não encontrado.")

arquivo = arquivos[0]

abas = {
    "Escola": "Tabela_de_Escola",
    "Matricula": "Tabela_de_Matrícula",
    "Docente": "Tabela_de_Docente",
}

palavras_chave = [
    "alter",
    "renome",
    "antigo nome",
    "descontinu",
    "retirad",
    "incluíd",
    "incluida",
    "incluído",
    "incluido",
    "a partir de",
    "substitu",
]

resultado = []

for tabela, aba in abas.items():

    df = pd.read_excel(
        arquivo,
        sheet_name=aba,
        header=None
    )

    for _, linha in df.iloc[9:].iterrows():

        variavel = linha.iloc[1]

        if pd.isna(variavel):
            continue

        notas = linha.iloc[25]

        if pd.isna(notas):
            continue

        notas_texto = str(notas)

        if any(
            palavra.lower() in notas_texto.lower()
            for palavra in palavras_chave
        ):
            resultado.append({
                "tabela": tabela,
                "variavel": variavel,
                "descricao": linha.iloc[2],
                "notas_importantes": notas_texto
            })

df_resultado = pd.DataFrame(resultado)

saida = OUTPUT_DIR / "comparabilidade_historica_notas.csv"

df_resultado.to_csv(
    saida,
    index=False,
    encoding="utf-8-sig"
)

print("=" * 80)
print("VARIÁVEIS COM NOTAS RELEVANTES PARA COMPARABILIDADE")
print("=" * 80)

print(f"\nTotal identificado: {len(df_resultado)}")

print("\nQuantidade por tabela:")
print(
    df_resultado
    .groupby("tabela")
    .size()
    .to_string()
)

print("\nVariáveis identificadas:\n")

for tabela in abas:
    variaveis = df_resultado[
        df_resultado["tabela"] == tabela
    ]["variavel"]

    print(f"\n{tabela}:")
    for variavel in variaveis:
        print(f"- {variavel}")

print(f"\nArquivo gerado:")
print(saida)