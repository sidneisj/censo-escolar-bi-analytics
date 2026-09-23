import pandas as pd
from pathlib import Path


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
# Issue #29 — Gerar e validar a base final para o Tableau
#
# Objetivos:
#
# 1. validar a base histórica consolidada produzida na issue #28;
# 2. verificar regras de qualidade importantes para consumo no Tableau;
# 3. gerar uma camada final de publicação sem alterar o grão dos dados;
# 4. reler o CSV exportado e confirmar que a gravação não provocou alterações;
# 5. gerar relatórios finais de validação e resumo da base.
#
# GRÃO FINAL:
#
#     uma linha por Escola × Ano
#
# PERÍODO:
#
#     2019 a 2025
#
# A base não será agregada previamente. Isso preserva a capacidade de análise
# por Região, UF, Município, dependência administrativa, localização e
# infraestrutura dentro do Tableau.


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
EXPLORACAO_DIR = BASE_DIR / "documentation" / "exploracao"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
EXPLORACAO_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# ARQUIVOS
# =============================================================================

ARQUIVO_ORIGEM = (
    PROCESSED_DIR /
    "censo_escolar_2019_2025_consolidado.csv"
)

ARQUIVO_TABLEAU = (
    PROCESSED_DIR /
    "censo_escolar_tableau_2019_2025.csv"
)

ARQUIVO_VALIDACAO = (
    EXPLORACAO_DIR /
    "validacao_base_tableau_2019_2025.csv"
)

ARQUIVO_RESUMO = (
    EXPLORACAO_DIR /
    "resumo_base_tableau_2019_2025.csv"
)


# =============================================================================
# ESTRUTURA ESPERADA
# =============================================================================

COLUNAS_ESPERADAS = [
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
    "QT_MAT_BAS",
    "QT_DOC_BAS",

    "ID_ANO_ENTIDADE",
    "DS_DEPENDENCIA",
    "DS_REDE",
    "DS_LOCALIZACAO",
    "DS_SITUACAO_FUNCIONAMENTO",
    "FL_ESCOLA_ATIVA",
]


COLUNAS_INFRAESTRUTURA = [
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
]


COLUNAS_QUANTITATIVAS = [
    "QT_SALAS_UTILIZADAS",
    "QT_MAT_BAS",
    "QT_DOC_BAS",
]


# =============================================================================
# MAPEAMENTOS ESPERADOS
# =============================================================================

MAPA_DEPENDENCIA = {
    1: "Federal",
    2: "Estadual",
    3: "Municipal",
    4: "Privada",
}

MAPA_REDE = {
    1: "Pública",
    2: "Pública",
    3: "Pública",
    4: "Privada",
}

MAPA_LOCALIZACAO = {
    1: "Urbana",
    2: "Rural",
}

MAPA_SITUACAO = {
    1: "Em Atividade",
    2: "Paralisada",
    3: "Extinta (ano do Censo)",
    4: "Extinta em Anos Anteriores",
}


# =============================================================================
# LEITURA
# =============================================================================

def ler_base(caminho):
    """
    Lê a base preservando os códigos geográficos e identificadores como texto.
    """

    return pd.read_csv(
        caminho,
        encoding="utf-8-sig",
        dtype={
            "CO_ENTIDADE": "string",
            "CO_REGIAO": "string",
            "CO_UF": "string",
            "CO_MUNICIPIO": "string",
            "ID_ANO_ENTIDADE": "string",
        },
        low_memory=False
    )


# =============================================================================
# REGISTRO DOS TESTES
# =============================================================================

resultados = []


def registrar(grupo, teste, esperado, observado, valido):
    """
    Registra o resultado de uma validação.
    """

    resultados.append({
        "grupo": grupo,
        "teste": teste,
        "esperado": str(esperado),
        "observado": str(observado),
        "status": "OK" if valido else "REVISAR",
    })


# =============================================================================
# LEITURA DA BASE CONSOLIDADA
# =============================================================================

print("=" * 80)
print("GERAÇÃO E VALIDAÇÃO DA BASE FINAL PARA TABLEAU")
print("=" * 80)


if not ARQUIVO_ORIGEM.exists():
    raise FileNotFoundError(
        f"Base consolidada não encontrada: {ARQUIVO_ORIGEM}"
    )


df = ler_base(
    ARQUIVO_ORIGEM
)


print(f"\nRegistros de origem: {len(df):,}")
print(f"Colunas de origem:   {len(df.columns)}")


# =============================================================================
# 1. ESTRUTURA
# =============================================================================

print("\n--- Estrutura ---")


estrutura_ok = (
    list(df.columns) ==
    COLUNAS_ESPERADAS
)


print(
    f"Colunas esperadas: {len(COLUNAS_ESPERADAS)}"
)

print(
    f"Colunas encontradas: {len(df.columns)}"
)

print(
    f"Status: {'OK' if estrutura_ok else 'REVISAR'}"
)


registrar(
    "Estrutura",
    "Estrutura e ordem das colunas",
    COLUNAS_ESPERADAS,
    list(df.columns),
    estrutura_ok
)


# =============================================================================
# 2. PERÍODO
# =============================================================================

anos_esperados = list(
    range(2019, 2026)
)

anos_encontrados = sorted(
    pd.to_numeric(
        df["NU_ANO_CENSO"],
        errors="coerce"
    )
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)

periodo_ok = (
    anos_encontrados ==
    anos_esperados
)


registrar(
    "Período",
    "Anos presentes",
    anos_esperados,
    anos_encontrados,
    periodo_ok
)


print("\n--- Período ---")
print(f"Anos: {anos_encontrados}")
print(
    f"Status: {'OK' if periodo_ok else 'REVISAR'}"
)


# =============================================================================
# 3. CHAVES
# =============================================================================

chaves_nulas = (
    df[
        [
            "NU_ANO_CENSO",
            "CO_ENTIDADE",
            "ID_ANO_ENTIDADE",
        ]
    ]
    .isna()
    .any(axis=1)
    .sum()
)


chaves_duplicadas = (
    df["ID_ANO_ENTIDADE"]
    .duplicated()
    .sum()
)


registrar(
    "Chaves",
    "Chaves nulas",
    0,
    chaves_nulas,
    chaves_nulas == 0
)

registrar(
    "Chaves",
    "ID_ANO_ENTIDADE duplicada",
    0,
    chaves_duplicadas,
    chaves_duplicadas == 0
)


print("\n--- Chaves ---")

print(
    f"Chaves nulas:      "
    f"{chaves_nulas:,}"
)

print(
    f"Chaves duplicadas: "
    f"{chaves_duplicadas:,}"
)


# =============================================================================
# 4. CATEGORIAS OFICIAIS
# =============================================================================

print("\n--- Categorias oficiais ---")


categorias_validas = {
    "TP_DEPENDENCIA": {1, 2, 3, 4},
    "TP_LOCALIZACAO": {1, 2},
    "TP_SITUACAO_FUNCIONAMENTO": {1, 2, 3},
}


for coluna, esperado in categorias_validas.items():

    encontrados = set(
        pd.to_numeric(
            df[coluna],
            errors="coerce"
        )
        .dropna()
        .astype(int)
        .unique()
    )

    valido = (
        encontrados <= esperado
    )

    registrar(
        "Categorias",
        f"Domínio {coluna}",
        sorted(esperado),
        sorted(encontrados),
        valido
    )

    print(
        f"{coluna:<35} "
        f"{sorted(encontrados)} | "
        f"{'OK' if valido else 'REVISAR'}"
    )


# =============================================================================
# 5. INFRAESTRUTURA
# =============================================================================
# Indicadores de infraestrutura devem conter somente:
#
# 0 = Não
# 1 = Sim
# NA = não aplicável / informação ausente segundo a fonte.


print("\n--- Infraestrutura ---")


for coluna in COLUNAS_INFRAESTRUTURA:

    valores = set(
        pd.to_numeric(
            df[coluna],
            errors="coerce"
        )
        .dropna()
        .astype(int)
        .unique()
    )

    valido = (
        valores <= {0, 1}
    )

    registrar(
        "Infraestrutura",
        f"Domínio {coluna}",
        [0, 1, "NA"],
        sorted(valores),
        valido
    )

    print(
        f"{coluna:<35} "
        f"{sorted(valores)} | "
        f"{'OK' if valido else 'REVISAR'}"
    )


# =============================================================================
# 6. VALORES QUANTITATIVOS
# =============================================================================

print("\n--- Indicadores quantitativos ---")


for coluna in COLUNAS_QUANTITATIVAS:

    serie = pd.to_numeric(
        df[coluna],
        errors="coerce"
    )

    negativos = (
        serie < 0
    ).sum()

    especiais_88888 = (
        serie == 88888
    ).sum()

    registrar(
        "Quantitativos",
        f"Valores negativos em {coluna}",
        0,
        negativos,
        negativos == 0
    )

    registrar(
        "Quantitativos",
        f"Código especial 88888 em {coluna}",
        0,
        especiais_88888,
        especiais_88888 == 0
    )


    print(
        f"{coluna:<25} "
        f"Negativos: {negativos:,} | "
        f"88888: {especiais_88888:,}"
    )


# =============================================================================
# 7. VARIÁVEIS DERIVADAS
# =============================================================================

print("\n--- Variáveis derivadas ---")


# -----------------------------------------------------------------------------
# DS_DEPENDENCIA
# -----------------------------------------------------------------------------

esperado = (
    pd.to_numeric(
        df["TP_DEPENDENCIA"],
        errors="coerce"
    )
    .map(MAPA_DEPENDENCIA)
)

inconsistencias = (
    esperado.astype("string") !=
    df["DS_DEPENDENCIA"].astype("string")
).sum()


registrar(
    "Derivadas",
    "Consistência DS_DEPENDENCIA",
    0,
    inconsistencias,
    inconsistencias == 0
)

print(
    f"Inconsistências DS_DEPENDENCIA: "
    f"{inconsistencias:,}"
)


# -----------------------------------------------------------------------------
# DS_REDE
# -----------------------------------------------------------------------------

esperado = (
    pd.to_numeric(
        df["TP_DEPENDENCIA"],
        errors="coerce"
    )
    .map(MAPA_REDE)
)

inconsistencias = (
    esperado.astype("string") !=
    df["DS_REDE"].astype("string")
).sum()


registrar(
    "Derivadas",
    "Consistência DS_REDE",
    0,
    inconsistencias,
    inconsistencias == 0
)

print(
    f"Inconsistências DS_REDE: "
    f"{inconsistencias:,}"
)


# -----------------------------------------------------------------------------
# DS_LOCALIZACAO
# -----------------------------------------------------------------------------

esperado = (
    pd.to_numeric(
        df["TP_LOCALIZACAO"],
        errors="coerce"
    )
    .map(MAPA_LOCALIZACAO)
)

inconsistencias = (
    esperado.astype("string") !=
    df["DS_LOCALIZACAO"].astype("string")
).sum()


registrar(
    "Derivadas",
    "Consistência DS_LOCALIZACAO",
    0,
    inconsistencias,
    inconsistencias == 0
)

print(
    f"Inconsistências DS_LOCALIZACAO: "
    f"{inconsistencias:,}"
)


# -----------------------------------------------------------------------------
# DS_SITUACAO_FUNCIONAMENTO
# -----------------------------------------------------------------------------

esperado = (
    pd.to_numeric(
        df["TP_SITUACAO_FUNCIONAMENTO"],
        errors="coerce"
    )
    .map(MAPA_SITUACAO)
)

inconsistencias = (
    esperado.astype("string") !=
    df["DS_SITUACAO_FUNCIONAMENTO"].astype("string")
).sum()


registrar(
    "Derivadas",
    "Consistência DS_SITUACAO_FUNCIONAMENTO",
    0,
    inconsistencias,
    inconsistencias == 0
)

print(
    f"Inconsistências DS_SITUACAO_FUNCIONAMENTO: "
    f"{inconsistencias:,}"
)


# -----------------------------------------------------------------------------
# FL_ESCOLA_ATIVA
# -----------------------------------------------------------------------------

esperado = (
    pd.to_numeric(
        df["TP_SITUACAO_FUNCIONAMENTO"],
        errors="coerce"
    ) == 1
).astype(int)


observado = pd.to_numeric(
    df["FL_ESCOLA_ATIVA"],
    errors="coerce"
)


inconsistencias = (
    esperado != observado
).sum()


registrar(
    "Derivadas",
    "Consistência FL_ESCOLA_ATIVA",
    0,
    inconsistencias,
    inconsistencias == 0
)

print(
    f"Inconsistências FL_ESCOLA_ATIVA: "
    f"{inconsistencias:,}"
)


# =============================================================================
# 8. VALIDAÇÃO PRÉ-EXPORTAÇÃO
# =============================================================================

df_resultados_parcial = pd.DataFrame(
    resultados
)


problemas = (
    df_resultados_parcial["status"] ==
    "REVISAR"
).sum()


if problemas > 0:

    df_resultados_parcial.to_csv(
        ARQUIVO_VALIDACAO,
        index=False,
        encoding="utf-8-sig"
    )

    raise ValueError(
        f"Foram encontrados {problemas} teste(s) "
        f"com status REVISAR. "
        f"A base Tableau não será gerada."
    )


# =============================================================================
# 9. GERAÇÃO DA BASE TABLEAU
# =============================================================================
# Não são realizadas novas transformações semânticas.
#
# A camada Tableau representa a versão final validada e ordenada da base
# consolidada.


print("\n--- Gerando base Tableau ---")


df_tableau = (
    df[
        COLUNAS_ESPERADAS
    ]
    .sort_values(
        [
            "NU_ANO_CENSO",
            "CO_ENTIDADE",
        ]
    )
    .reset_index(drop=True)
)


df_tableau.to_csv(
    ARQUIVO_TABLEAU,
    index=False,
    encoding="utf-8-sig"
)


print(
    f"Arquivo gerado com "
    f"{len(df_tableau):,} registros."
)


# =============================================================================
# 10. RELEITURA DO ARQUIVO EXPORTADO
# =============================================================================
# Esta etapa garante que a serialização para CSV não alterou o conteúdo
# necessário para o Tableau.


df_exportado = ler_base(
    ARQUIVO_TABLEAU
)


# -----------------------------------------------------------------------------
# Registros
# -----------------------------------------------------------------------------

registrar(
    "Exportação",
    "Quantidade de registros após releitura",
    len(df_tableau),
    len(df_exportado),
    len(df_tableau) == len(df_exportado)
)


# -----------------------------------------------------------------------------
# Colunas
# -----------------------------------------------------------------------------

registrar(
    "Exportação",
    "Quantidade de colunas após releitura",
    len(df_tableau.columns),
    len(df_exportado.columns),
    len(df_tableau.columns) == len(df_exportado.columns)
)


# -----------------------------------------------------------------------------
# Chaves
# -----------------------------------------------------------------------------

duplicados_exportados = (
    df_exportado["ID_ANO_ENTIDADE"]
    .duplicated()
    .sum()
)


registrar(
    "Exportação",
    "Chaves duplicadas após releitura",
    0,
    duplicados_exportados,
    duplicados_exportados == 0
)


# -----------------------------------------------------------------------------
# Totais quantitativos
# -----------------------------------------------------------------------------

for coluna in COLUNAS_QUANTITATIVAS:

    total_antes = pd.to_numeric(
        df_tableau[coluna],
        errors="coerce"
    ).sum()

    total_depois = pd.to_numeric(
        df_exportado[coluna],
        errors="coerce"
    ).sum()

    registrar(
        "Exportação",
        f"Total preservado {coluna}",
        total_antes,
        total_depois,
        total_antes == total_depois
    )


# -----------------------------------------------------------------------------
# Nulos quantitativos
# -----------------------------------------------------------------------------

for coluna in COLUNAS_QUANTITATIVAS:

    nulos_antes = (
        df_tableau[coluna]
        .isna()
        .sum()
    )

    nulos_depois = (
        df_exportado[coluna]
        .isna()
        .sum()
    )

    registrar(
        "Exportação",
        f"Nulos preservados {coluna}",
        nulos_antes,
        nulos_depois,
        nulos_antes == nulos_depois
    )


# =============================================================================
# 11. RESUMO ANALÍTICO PARA O TABLEAU
# =============================================================================

resumo = (
    df_exportado
    .groupby(
        "NU_ANO_CENSO",
        as_index=False
    )
    .agg(
        registros=(
            "ID_ANO_ENTIDADE",
            "size"
        ),

        entidades=(
            "CO_ENTIDADE",
            "nunique"
        ),

        escolas_ativas=(
            "FL_ESCOLA_ATIVA",
            "sum"
        ),

        matriculas=(
            "QT_MAT_BAS",
            "sum"
        ),

        docentes=(
            "QT_DOC_BAS",
            "sum"
        ),

        salas_utilizadas=(
            "QT_SALAS_UTILIZADAS",
            "sum"
        ),
    )
)


resumo.to_csv(
    ARQUIVO_RESUMO,
    index=False,
    encoding="utf-8-sig"
)


# =============================================================================
# 12. RELATÓRIO FINAL
# =============================================================================

df_resultados = pd.DataFrame(
    resultados
)


df_resultados.to_csv(
    ARQUIVO_VALIDACAO,
    index=False,
    encoding="utf-8-sig"
)


testes_ok = (
    df_resultados["status"] == "OK"
).sum()

testes_revisar = (
    df_resultados["status"] == "REVISAR"
).sum()


print("\n" + "=" * 80)
print("RESUMO DA BASE TABLEAU")
print("=" * 80)

print(
    resumo.to_string(
        index=False
    )
)


print("\n" + "=" * 80)
print("VALIDAÇÃO FINAL")
print("=" * 80)

print(
    f"Registros:       "
    f"{len(df_exportado):,}"
)

print(
    f"Colunas:         "
    f"{len(df_exportado.columns)}"
)

print(
    f"Testes OK:       "
    f"{testes_ok}"
)

print(
    f"Testes REVISAR:  "
    f"{testes_revisar}"
)


if testes_revisar == 0:

    print("\nSTATUS FINAL: OK")

else:

    print("\nSTATUS FINAL: REVISAR")


print("\nArquivos gerados:")

print(ARQUIVO_TABLEAU)
print(ARQUIVO_VALIDACAO)
print(ARQUIVO_RESUMO)


print("\n" + "=" * 80)
print("Base final para Tableau concluída.")
print("=" * 80)