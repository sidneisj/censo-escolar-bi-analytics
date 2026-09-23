import pandas as pd
from pathlib import Path


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
# Este script realiza a primeira etapa da harmonização histórica.
#
# Objetivo:
#
# - identificar a estrutura dos arquivos de 2019 a 2025;
# - verificar quais variáveis selecionadas para o projeto existem em cada ano;
# - identificar variáveis ausentes;
# - comparar a estrutura histórica com a nova organização adotada em 2025.
#
# IMPORTANTE:
# Os arquivos históricos possuem aproximadamente 200 MB.
#
# Para esta análise são lidos apenas os cabeçalhos dos CSVs (nrows=0),
# evitando o carregamento completo dos dados em memória.


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
EXPLORACAO_DIR = BASE_DIR / "documentation" / "exploracao"

EXPLORACAO_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# ARQUIVOS HISTÓRICOS
# =============================================================================
# Entre 2019 e 2024 o Censo Escolar utiliza um único arquivo principal com
# informações agregadas por estabelecimento.
#
# Em 2025, as informações passaram a estar organizadas em diferentes tabelas.
#
# Nesta análise utilizamos:
#
# - Escola 2025 para dimensões e infraestrutura;
# - Matrícula 2025 para QT_MAT_BAS;
# - Docente 2025 para QT_DOC_BAS.


ARQUIVOS_HISTORICOS = {
    2019: RAW_DIR / "microdados_ed_basica_2019.csv",
    2020: RAW_DIR / "microdados_ed_basica_2020.csv",
    2021: RAW_DIR / "microdados_ed_basica_2021.csv",
    2022: RAW_DIR / "microdados_ed_basica_2022.csv",
    2023: RAW_DIR / "microdados_ed_basica_2023.csv",
    2024: RAW_DIR / "microdados_ed_basica_2024.csv",
}


ARQUIVOS_2025 = {
    "Escola": RAW_DIR / "Tabela_Escola_2025_V2.csv",
    "Matricula": RAW_DIR / "Tabela_Matricula_2025_V2.csv",
    "Docente": RAW_DIR / "Tabela_Docente_2025_V2.csv",
}


# =============================================================================
# VARIÁVEIS NECESSÁRIAS PARA O PROJETO
# =============================================================================
# A lista utiliza a seleção definida na issue #21.
#
# Para os anos de 2019 a 2024 esperamos encontrar essas informações no
# arquivo único de Microdados da Educação Básica.


VARIAVEIS_ESCOLA = [
    "NU_ANO_CENSO",
    "CO_ENTIDADE",
    "NO_ENTIDADE",

    "CO_REGIAO",
    "NO_REGIAO",

    "CO_UF",
    "SG_UF",
    "NO_UF",

    "CO_MUNICIPIO",
    "NO_MUNICIPIO",

    "TP_DEPENDENCIA",
    "TP_LOCALIZACAO",
    "TP_SITUACAO_FUNCIONAMENTO",

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


VARIAVEIS_INDICADORES = [
    "QT_MAT_BAS",
    "QT_DOC_BAS",
]


VARIAVEIS_PROJETO = (
    VARIAVEIS_ESCOLA
    + VARIAVEIS_INDICADORES
)


# =============================================================================
# FUNÇÃO PARA LEITURA DO CABEÇALHO
# =============================================================================

def ler_cabecalho(caminho):
    """
    Lê somente o cabeçalho de um arquivo CSV.

    São testadas as codificações mais comuns encontradas nos arquivos do INEP.

    O parâmetro nrows=0 garante que nenhuma linha de dados seja carregada.
    """

    tentativas = [
        "utf-8-sig",
        "latin-1",
        "cp1252",
    ]

    ultimo_erro = None

    for encoding in tentativas:

        try:

            df = pd.read_csv(
                caminho,
                sep=";",
                encoding=encoding,
                nrows=0
            )

            return list(df.columns), encoding

        except UnicodeDecodeError as erro:

            ultimo_erro = erro

    raise ultimo_erro


# =============================================================================
# RESULTADOS
# =============================================================================

resultados = []


print("=" * 80)
print("ANÁLISE DA ESTRUTURA HISTÓRICA")
print("=" * 80)


# =============================================================================
# 2019 A 2024
# =============================================================================

for ano, arquivo in ARQUIVOS_HISTORICOS.items():

    print(f"\n{'=' * 80}")
    print(ano)
    print("=" * 80)

    if not arquivo.exists():

        print(f"ERRO: arquivo não encontrado: {arquivo.name}")
        continue


    colunas, encoding = ler_cabecalho(arquivo)

    conjunto_colunas = set(colunas)

    encontradas = [
        variavel
        for variavel in VARIAVEIS_PROJETO
        if variavel in conjunto_colunas
    ]

    ausentes = [
        variavel
        for variavel in VARIAVEIS_PROJETO
        if variavel not in conjunto_colunas
    ]


    print(f"Arquivo:             {arquivo.name}")
    print(f"Encoding:            {encoding}")
    print(f"Total de colunas:    {len(colunas)}")

    print(
        f"Variáveis esperadas: {len(VARIAVEIS_PROJETO)}"
    )

    print(
        f"Encontradas:         {len(encontradas)}"
    )

    print(
        f"Ausentes:            {len(ausentes)}"
    )


    if ausentes:

        print("\nVariáveis ausentes:")

        for variavel in ausentes:
            print(f"- {variavel}")

    else:

        print("\nTodas as variáveis selecionadas estão disponíveis.")


    # -------------------------------------------------------------------------
    # Registro detalhado
    # -------------------------------------------------------------------------

    for variavel in VARIAVEIS_PROJETO:

        resultados.append({
            "ano": ano,
            "origem": "microdados_ed_basica",
            "variavel": variavel,
            "disponivel": (
                "Sim"
                if variavel in conjunto_colunas
                else "Não"
            )
        })


# =============================================================================
# ESTRUTURA 2025
# =============================================================================

print(f"\n{'=' * 80}")
print("2025")
print("=" * 80)


colunas_2025 = set()


for tabela, arquivo in ARQUIVOS_2025.items():

    if not arquivo.exists():

        print(
            f"ERRO: arquivo não encontrado: "
            f"{arquivo.name}"
        )

        continue


    colunas, encoding = ler_cabecalho(arquivo)

    print(
        f"{tabela:<12} "
        f"{len(colunas):>4} colunas | "
        f"{encoding}"
    )

    colunas_2025.update(colunas)


encontradas_2025 = [
    variavel
    for variavel in VARIAVEIS_PROJETO
    if variavel in colunas_2025
]

ausentes_2025 = [
    variavel
    for variavel in VARIAVEIS_PROJETO
    if variavel not in colunas_2025
]


print(
    f"\nVariáveis esperadas: "
    f"{len(VARIAVEIS_PROJETO)}"
)

print(
    f"Encontradas:         "
    f"{len(encontradas_2025)}"
)

print(
    f"Ausentes:            "
    f"{len(ausentes_2025)}"
)


if ausentes_2025:

    print("\nVariáveis ausentes em 2025:")

    for variavel in ausentes_2025:
        print(f"- {variavel}")

else:

    print(
        "\nTodas as variáveis selecionadas "
        "estão disponíveis em 2025."
    )


for variavel in VARIAVEIS_PROJETO:

    resultados.append({
        "ano": 2025,
        "origem": "tabelas_separadas",
        "variavel": variavel,
        "disponivel": (
            "Sim"
            if variavel in colunas_2025
            else "Não"
        )
    })


# =============================================================================
# GERAÇÃO DA MATRIZ DE DISPONIBILIDADE
# =============================================================================

df_resultados = pd.DataFrame(resultados)


matriz = (
    df_resultados
    .pivot(
        index="variavel",
        columns="ano",
        values="disponivel"
    )
    .reset_index()
)


arquivo_saida = (
    EXPLORACAO_DIR /
    "disponibilidade_variaveis_2019_2025.csv"
)


matriz.to_csv(
    arquivo_saida,
    index=False,
    encoding="utf-8-sig"
)


# =============================================================================
# RESUMO
# =============================================================================

print("\n" + "=" * 80)
print("RESUMO DE DISPONIBILIDADE")
print("=" * 80)


for ano in range(2019, 2026):

    dados_ano = df_resultados[
        df_resultados["ano"] == ano
    ]

    disponiveis = (
        dados_ano["disponivel"] == "Sim"
    ).sum()

    ausentes = (
        dados_ano["disponivel"] == "Não"
    ).sum()

    print(
        f"{ano}: "
        f"{disponiveis} disponíveis | "
        f"{ausentes} ausentes"
    )


print(f"\nMatriz gerada:")
print(arquivo_saida)

print("\nAnálise concluída.")