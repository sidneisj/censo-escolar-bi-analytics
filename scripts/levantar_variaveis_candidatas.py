import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTATION = BASE_DIR / "documentation" / "inep"
EXPLORACAO = BASE_DIR / "documentation" / "exploracao"

EXPLORACAO.mkdir(parents=True, exist_ok=True)

arquivos = list(DOCUMENTATION.glob("*dicion*.xlsx"))

if not arquivos:
    raise FileNotFoundError(
        "Dicionário de dados não encontrado em documentation/inep/"
    )

arquivo_dicionario = arquivos[0]

abas = {
    "Escola": "Tabela_de_Escola",
    "Matricula": "Tabela_de_Matrícula",
    "Docente": "Tabela_de_Docente",
}

# Variáveis comuns às três tabelas
identificacao = [
    "NU_ANO_CENSO",
    "NO_ENTIDADE",
    "CO_ENTIDADE",
]

geografia = [
    "NO_REGIAO",
    "CO_REGIAO",
    "NO_UF",
    "SG_UF",
    "CO_UF",
    "NO_MUNICIPIO",
    "CO_MUNICIPIO",
]

segmentacao = [
    "TP_DEPENDENCIA",
    "TP_CATEGORIA_ESCOLA_PRIVADA",
    "TP_LOCALIZACAO",
    "TP_LOCALIZACAO_DIFERENCIADA",
]

# Variáveis específicas
escola = [
    "TP_SITUACAO_FUNCIONAMENTO",

    # Infraestrutura
    "IN_INTERNET",
    "IN_BIBLIOTECA",
    "IN_SALA_LEITURA",
    "IN_LABORATORIO_CIENCIAS",
    "IN_LABORATORIO_INFORMATICA",
    "IN_QUADRA_ESPORTES",
    "IN_BANHEIRO_PNE",
    "IN_ACESSIBILIDADE_INEXISTENTE",
    "IN_AGUA_POTAVEL",
    "IN_ESGOTO_REDE_PUBLICA",
    "IN_ENERGIA_REDE_PUBLICA",
    "QT_SALAS_UTILIZADAS",
]

matricula = [
    "QT_MAT_BAS",
]

docente = [
    "QT_DOC_BAS",
]

configuracao = {
    "Escola": {
        "Identificação": identificacao,
        "Geografia": geografia,
        "Segmentação": segmentacao,
        "Controle": ["TP_SITUACAO_FUNCIONAMENTO"],
        "Infraestrutura": escola[1:],
    },
    "Matricula": {
        "Identificação": identificacao,
        "Geografia": geografia,
        "Segmentação": segmentacao,
        "Indicador": matricula,
    },
    "Docente": {
        "Identificação": identificacao,
        "Geografia": geografia,
        "Segmentação": segmentacao,
        "Indicador": docente,
    },
}

resultado = []

for tabela, grupos in configuracao.items():

    df = pd.read_excel(
        arquivo_dicionario,
        sheet_name=abas[tabela],
        header=None
    )

    # Variáveis começam na linha 10 do Excel
    df = df.iloc[9:].copy()

    for grupo, variaveis in grupos.items():

        for variavel in variaveis:

            linha = df[df.iloc[:, 1] == variavel]

            if linha.empty:
                print(
                    f"ATENÇÃO: {variavel} não encontrada "
                    f"na tabela {tabela}"
                )
                continue

            linha = linha.iloc[0]

            resultado.append({
                "tabela": tabela,
                "grupo": grupo,
                "variavel": variavel,
                "descricao": linha.iloc[2],
                "tipo": linha.iloc[3],
                "categoria": linha.iloc[5],
                "coleta_2025": linha.iloc[24],
                "notas_importantes": linha.iloc[25],
            })


df_resultado = pd.DataFrame(resultado)

# ------------------------------------------------
# Cruzamento com a análise da issue #20
# ------------------------------------------------

arquivo_comparabilidade = (
    EXPLORACAO / "comparabilidade_historica.csv"
)

if arquivo_comparabilidade.exists():

    comparabilidade = pd.read_csv(
        arquivo_comparabilidade,
        encoding="utf-8-sig"
    )

    comparabilidade = comparabilidade[
        [
            "tabela",
            "variavel",
            "primeiro_ano",
            "ultimo_ano",
            "status_coleta",
            "comparabilidade_preliminar",
        ]
    ]

    df_resultado = df_resultado.merge(
        comparabilidade,
        on=["tabela", "variavel"],
        how="left"
    )

# ------------------------------------------------
# Salvar resultado
# ------------------------------------------------

saida = EXPLORACAO / "variaveis_candidatas.csv"

df_resultado.to_csv(
    saida,
    index=False,
    encoding="utf-8-sig"
)

print("=" * 80)
print("VARIÁVEIS CANDIDATAS PARA O PROJETO")
print("=" * 80)

print("\nQuantidade por tabela:")

print(
    df_resultado
    .groupby("tabela")
    .size()
    .to_string()
)

print("\nQuantidade por grupo:")

print(
    df_resultado
    .groupby(["tabela", "grupo"])
    .size()
    .to_string()
)

print("\nVariáveis candidatas:")

for tabela in configuracao:

    print(f"\n--- {tabela} ---")

    dados = df_resultado[
        df_resultado["tabela"] == tabela
    ]

    for _, linha in dados.iterrows():
        print(
            f"{linha['grupo']:<16} "
            f"{linha['variavel']}"
        )

print(f"\nArquivo gerado:")
print(saida)

print("\nLevantamento concluído.")
