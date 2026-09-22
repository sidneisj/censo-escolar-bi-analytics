import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTATION = BASE_DIR / "documentation" / "inep"
OUTPUT_DIR = BASE_DIR / "documentation" / "exploracao"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Localiza automaticamente o dicionário
arquivos = list(DOCUMENTATION.glob("*dicion*.xlsx"))

if not arquivos:
    raise FileNotFoundError(
        "Dicionário de dados não encontrado em documentation/inep/"
    )

arquivo = arquivos[0]

abas = {
    "Escola": "Tabela_de_Escola",
    "Matricula": "Tabela_de_Matrícula",
    "Docente": "Tabela_de_Docente",
}

anos = list(range(2007, 2026))


def classificar_coleta(valores):
    coletados = [
        ano
        for ano, valor in zip(anos, valores)
        if str(valor).strip().lower() == "s"
    ]

    if not coletados:
        return None, None, "Sem coleta no período"

    primeiro = min(coletados)
    ultimo = max(coletados)

    intervalo = list(range(primeiro, ultimo + 1))

    if coletados == anos:
        status = "Coleta contínua 2007-2025"

    elif coletados == intervalo and ultimo == 2025:
        status = f"Coleta iniciada em {primeiro}"

    elif coletados == intervalo and primeiro == 2007:
        status = f"Descontinuada após {ultimo}"

    elif coletados == intervalo:
        status = f"Coleta contínua de {primeiro} a {ultimo}"

    else:
        status = "Coleta intermitente / revisar"

    return primeiro, ultimo, status


resultado = []

for tabela, aba in abas.items():

    df = pd.read_excel(
        arquivo,
        sheet_name=aba,
        header=None
    )

    # Os registros das variáveis começam na linha 10 do Excel
    for _, linha in df.iloc[9:].iterrows():

        nome_variavel = linha.iloc[1]

        if pd.isna(nome_variavel):
            continue

        descricao = linha.iloc[2]
        categoria = linha.iloc[5]

        # G até Y = 2007 a 2025
        coleta = linha.iloc[6:25].tolist()

        notas = linha.iloc[25] if len(linha) > 25 else None

        primeiro, ultimo, status = classificar_coleta(coleta)

        anos_nao_coletados = [
            str(ano)
            for ano, valor in zip(anos, coleta)
            if str(valor).strip().lower() != "s"
        ]

        if status == "Coleta contínua 2007-2025":
            comparabilidade = "Potencialmente comparável em toda a série"
        elif status == "Coleta intermitente / revisar":
            comparabilidade = "Comparabilidade restrita"
        else:
            comparabilidade = "Comparável apenas no período de coleta"

        resultado.append({
            "tabela": tabela,
            "variavel": nome_variavel,
            "descricao": descricao,
            "primeiro_ano": primeiro,
            "ultimo_ano": ultimo,
            "status_coleta": status,
            "anos_nao_coletados": ", ".join(anos_nao_coletados),
            "comparabilidade_preliminar": comparabilidade,
            "categoria": categoria,
            "notas_importantes": notas
        })


df_resultado = pd.DataFrame(resultado)

saida = OUTPUT_DIR / "comparabilidade_historica.csv"

df_resultado.to_csv(
    saida,
    index=False,
    encoding="utf-8-sig"
)

print("=" * 80)
print("COMPARABILIDADE HISTÓRICA")
print("=" * 80)

print("\nResumo por tabela e situação:\n")

resumo = (
    df_resultado
    .groupby(["tabela", "status_coleta"])
    .size()
    .reset_index(name="quantidade")
)

print(resumo.to_string(index=False))

print(f"\nArquivo gerado:")
print(saida)

print("\nAnálise concluída.")