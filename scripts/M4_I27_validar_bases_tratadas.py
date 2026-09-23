import pandas as pd
from pathlib import Path


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
# Este script realiza a validação final das bases tratadas do Censo Escolar
# 2025 antes da etapa de consolidação histórica.
#
# A validação compara os arquivos originais do INEP com as bases resultantes
# do processo de ETL.
#
# São verificados:
#
# - quantidade de registros;
# - estrutura esperada;
# - integridade das chaves;
# - ano de referência;
# - preservação dos principais indicadores quantitativos;
# - preservação das categorias oficiais;
# - valores ausentes de infraestrutura;
# - correção dos campos geográficos;
# - coerência das variáveis derivadas;
# - relacionamentos entre Escola, Matrícula e Docente.
#
# Nenhuma transformação é realizada neste script.


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
EXPLORACAO_DIR = BASE_DIR / "documentation" / "exploracao"

EXPLORACAO_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# ARQUIVOS ORIGINAIS
# =============================================================================

RAW = {
    "Escola": RAW_DIR / "Tabela_Escola_2025_V2.csv",
    "Matricula": RAW_DIR / "Tabela_Matricula_2025_V2.csv",
    "Docente": RAW_DIR / "Tabela_Docente_2025_V2.csv",
}


# =============================================================================
# BASES FINAIS DA ETAPA DE ETL
# =============================================================================
# Utilizamos os arquivos enriquecidos pela issue #26, que representam o
# estágio mais recente do pipeline.

FINAL = {
    "Escola": PROCESSED_DIR / "escola_2025_derivada.csv",
    "Matricula": PROCESSED_DIR / "matricula_2025_derivada.csv",
    "Docente": PROCESSED_DIR / "docente_2025_derivada.csv",
}


# =============================================================================
# COLUNAS ESPERADAS
# =============================================================================
# A validação garante que nenhuma variável necessária tenha sido perdida e
# que nenhuma coluna inesperada tenha sido adicionada às bases analíticas.

COLUNAS_ESPERADAS = {

    "Escola": [
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
        "ID_ANO_ENTIDADE",
        "DS_DEPENDENCIA",
        "DS_REDE",
        "DS_LOCALIZACAO",
        "DS_SITUACAO_FUNCIONAMENTO",
        "FL_ESCOLA_ATIVA",
    ],

    "Matricula": [
        "NU_ANO_CENSO",
        "CO_ENTIDADE",
        "QT_MAT_BAS",
        "ID_ANO_ENTIDADE",
    ],

    "Docente": [
        "NU_ANO_CENSO",
        "CO_ENTIDADE",
        "QT_DOC_BAS",
        "ID_ANO_ENTIDADE",
    ],
}


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def ler_raw(caminho, usecols=None):
    """
    Realiza a leitura dos arquivos originais do INEP.

    A função tenta UTF-8 e utiliza Latin-1 como alternativa caso necessário.
    """

    try:
        return pd.read_csv(
            caminho,
            sep=";",
            encoding="utf-8-sig",
            usecols=usecols,
            low_memory=False
        )

    except UnicodeDecodeError:
        return pd.read_csv(
            caminho,
            sep=";",
            encoding="latin-1",
            usecols=usecols,
            low_memory=False
        )


def ler_final(caminho):
    """
    Realiza a leitura das bases processadas pelo pipeline.
    """

    return pd.read_csv(
        caminho,
        encoding="utf-8-sig",
        dtype={
            "CO_ENTIDADE": "string",
            "ID_ANO_ENTIDADE": "string",
        },
        low_memory=False
    )


# Lista que armazenará todos os testes realizados.
resultados = []


def registrar_teste(tabela, grupo, teste, esperado, observado, valido):
    """
    Registra o resultado de cada validação para posterior geração
    do relatório consolidado.
    """

    resultados.append({
        "tabela": tabela,
        "grupo": grupo,
        "teste": teste,
        "esperado": str(esperado),
        "observado": str(observado),
        "status": "OK" if valido else "REVISAR",
    })


# =============================================================================
# LEITURA DAS BASES FINAIS
# =============================================================================

print("=" * 80)
print("VALIDAÇÃO FINAL DAS BASES TRATADAS")
print("=" * 80)


bases = {}

for tabela, arquivo in FINAL.items():

    bases[tabela] = ler_final(arquivo)


# =============================================================================
# 1. QUANTIDADE DE REGISTROS
# =============================================================================
# Nenhuma etapa realizada até aqui deveria eliminar ou adicionar registros.
#
# Portanto, as quantidades das bases finais devem ser idênticas às bases
# originais do INEP.

print("\n--- Quantidade de registros ---")

for tabela in FINAL:

    # Para economizar memória, basta carregar uma coluna do arquivo original.
    raw = ler_raw(
        RAW[tabela],
        usecols=["CO_ENTIDADE"]
    )

    quantidade_raw = len(raw)
    quantidade_final = len(bases[tabela])

    valido = quantidade_raw == quantidade_final

    registrar_teste(
        tabela,
        "Registros",
        "Quantidade de registros preservada",
        quantidade_raw,
        quantidade_final,
        valido
    )

    print(
        f"{tabela:<12} "
        f"RAW: {quantidade_raw:>8,} | "
        f"FINAL: {quantidade_final:>8,} | "
        f"{'OK' if valido else 'REVISAR'}"
    )


# =============================================================================
# 2. ESTRUTURA DAS BASES
# =============================================================================

print("\n--- Estrutura das bases ---")

for tabela, df in bases.items():

    colunas_encontradas = list(df.columns)
    colunas_esperadas = COLUNAS_ESPERADAS[tabela]

    valido = colunas_encontradas == colunas_esperadas

    registrar_teste(
        tabela,
        "Estrutura",
        "Colunas esperadas",
        len(colunas_esperadas),
        len(colunas_encontradas),
        valido
    )

    print(
        f"{tabela:<12} "
        f"{len(colunas_encontradas)} colunas | "
        f"{'OK' if valido else 'REVISAR'}"
    )


# =============================================================================
# 3. CHAVES
# =============================================================================

print("\n--- Integridade das chaves ---")

for tabela, df in bases.items():

    nulos = (
        df[["NU_ANO_CENSO", "CO_ENTIDADE", "ID_ANO_ENTIDADE"]]
        .isna()
        .any(axis=1)
        .sum()
    )

    duplicados = df["ID_ANO_ENTIDADE"].duplicated().sum()

    registrar_teste(
        tabela,
        "Chaves",
        "Chaves nulas",
        0,
        nulos,
        nulos == 0
    )

    registrar_teste(
        tabela,
        "Chaves",
        "ID_ANO_ENTIDADE duplicado",
        0,
        duplicados,
        duplicados == 0
    )

    print(
        f"{tabela:<12} "
        f"Nulos: {nulos:,} | "
        f"Duplicados: {duplicados:,}"
    )


# =============================================================================
# 4. ANO DE REFERÊNCIA
# =============================================================================

print("\n--- Ano de referência ---")

for tabela, df in bases.items():

    anos = sorted(
        pd.to_numeric(
            df["NU_ANO_CENSO"],
            errors="coerce"
        )
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    valido = anos == [2025]

    registrar_teste(
        tabela,
        "Período",
        "Ano de referência",
        [2025],
        anos,
        valido
    )

    print(
        f"{tabela:<12} "
        f"{anos} | "
        f"{'OK' if valido else 'REVISAR'}"
    )


# =============================================================================
# 5. PRESERVAÇÃO DOS PRINCIPAIS INDICADORES
# =============================================================================
# Comparamos os totais quantitativos da origem com as bases tratadas.
#
# O objetivo é garantir que as transformações não alteraram os valores dos
# principais indicadores utilizados no projeto.

print("\n--- Indicadores quantitativos ---")

INDICADORES = {
    "Escola": "QT_SALAS_UTILIZADAS",
    "Matricula": "QT_MAT_BAS",
    "Docente": "QT_DOC_BAS",
}


for tabela, coluna in INDICADORES.items():

    raw = ler_raw(
        RAW[tabela],
        usecols=[coluna]
    )

    total_raw = pd.to_numeric(
        raw[coluna],
        errors="coerce"
    ).sum()

    total_final = pd.to_numeric(
        bases[tabela][coluna],
        errors="coerce"
    ).sum()

    valido = total_raw == total_final

    registrar_teste(
        tabela,
        "Indicadores",
        f"Total de {coluna}",
        total_raw,
        total_final,
        valido
    )

    print(
        f"{tabela:<12} "
        f"{coluna:<25} "
        f"RAW: {total_raw:,.0f} | "
        f"FINAL: {total_final:,.0f} | "
        f"{'OK' if valido else 'REVISAR'}"
    )


# =============================================================================
# 6. PRESERVAÇÃO DAS CATEGORIAS OFICIAIS
# =============================================================================
# Verificamos se as principais categorias da tabela Escola mantiveram a mesma
# distribuição existente no arquivo original.

print("\n--- Categorias oficiais da tabela Escola ---")

CATEGORIAS = [
    "TP_DEPENDENCIA",
    "TP_LOCALIZACAO",
    "TP_SITUACAO_FUNCIONAMENTO",
]


raw_escola_categorias = ler_raw(
    RAW["Escola"],
    usecols=CATEGORIAS
)


for coluna in CATEGORIAS:

    raw_serie = pd.to_numeric(
        raw_escola_categorias[coluna],
        errors="coerce"
    )

    final_serie = pd.to_numeric(
        bases["Escola"][coluna],
        errors="coerce"
    )

    distribuicao_raw = (
        raw_serie
        .value_counts(dropna=False)
        .sort_index()
        .to_dict()
    )

    distribuicao_final = (
        final_serie
        .value_counts(dropna=False)
        .sort_index()
        .to_dict()
    )

    valido = distribuicao_raw == distribuicao_final

    registrar_teste(
        "Escola",
        "Categorias",
        f"Distribuição de {coluna}",
        distribuicao_raw,
        distribuicao_final,
        valido
    )

    print(
        f"{coluna:<35} "
        f"{'OK' if valido else 'REVISAR'}"
    )


# =============================================================================
# 7. INFRAESTRUTURA
# =============================================================================
# A issue #24 identificou que 33.652 registros possuem todas as informações
# de infraestrutura ausentes.
#
# Esses registros pertencem às situações de funcionamento 2 e 3.
#
# O padrão deve permanecer preservado.

print("\n--- Infraestrutura ---")

df_escola = bases["Escola"]

COLUNAS_INFRA = [
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


todas_nulas = (
    df_escola[COLUNAS_INFRA]
    .isna()
    .all(axis=1)
)

alguma_nula = (
    df_escola[COLUNAS_INFRA]
    .isna()
    .any(axis=1)
)

parcialmente_nulas = (
    alguma_nula & ~todas_nulas
).sum()

total_todas_nulas = todas_nulas.sum()


registrar_teste(
    "Escola",
    "Infraestrutura",
    "Registros com infraestrutura totalmente ausente",
    33652,
    total_todas_nulas,
    total_todas_nulas == 33652
)

registrar_teste(
    "Escola",
    "Infraestrutura",
    "Registros com infraestrutura parcialmente ausente",
    0,
    parcialmente_nulas,
    parcialmente_nulas == 0
)


print(
    f"Totalmente ausentes:   "
    f"{total_todas_nulas:,}"
)

print(
    f"Parcialmente ausentes: "
    f"{parcialmente_nulas:,}"
)


# =============================================================================
# 8. CAMPOS GEOGRÁFICOS
# =============================================================================
# O único problema geográfico identificado na issue #24 foi corrigido.
#
# Portanto, esses campos devem estar totalmente preenchidos na base final.

print("\n--- Geografia ---")

COLUNAS_GEO = [
    "NO_REGIAO",
    "SG_UF",
    "NO_UF",
    "NO_MUNICIPIO",
]


for coluna in COLUNAS_GEO:

    nulos = df_escola[coluna].isna().sum()

    registrar_teste(
        "Escola",
        "Geografia",
        f"Nulos em {coluna}",
        0,
        nulos,
        nulos == 0
    )

    print(
        f"{coluna:<25} "
        f"{nulos:,}"
    )


# =============================================================================
# 9. VARIÁVEIS DERIVADAS
# =============================================================================

print("\n--- Variáveis derivadas ---")


# -------------------------------------------------------------------------
# Rede pública / privada
# -------------------------------------------------------------------------

rede_esperada = df_escola["TP_DEPENDENCIA"].map({
    1: "Pública",
    2: "Pública",
    3: "Pública",
    4: "Privada",
})

inconsistencias_rede = (
    rede_esperada != df_escola["DS_REDE"]
).sum()


registrar_teste(
    "Escola",
    "Derivadas",
    "Coerência de DS_REDE",
    0,
    inconsistencias_rede,
    inconsistencias_rede == 0
)


# -------------------------------------------------------------------------
# Escola ativa
# -------------------------------------------------------------------------

ativa_esperada = (
    df_escola["TP_SITUACAO_FUNCIONAMENTO"] == 1
).astype(int)

inconsistencias_ativa = (
    ativa_esperada != df_escola["FL_ESCOLA_ATIVA"]
).sum()


registrar_teste(
    "Escola",
    "Derivadas",
    "Coerência de FL_ESCOLA_ATIVA",
    0,
    inconsistencias_ativa,
    inconsistencias_ativa == 0
)


print(
    f"Inconsistências DS_REDE:         "
    f"{inconsistencias_rede:,}"
)

print(
    f"Inconsistências FL_ESCOLA_ATIVA: "
    f"{inconsistencias_ativa:,}"
)


# =============================================================================
# 10. RELACIONAMENTOS ENTRE AS TABELAS
# =============================================================================
# Verificamos se todos os registros de Matrícula e Docente possuem uma escola
# correspondente na base Escola.
#
# A chave utilizada é ID_ANO_ENTIDADE.

print("\n--- Relacionamentos ---")

ids_escola = set(
    bases["Escola"]["ID_ANO_ENTIDADE"]
)

ids_matricula = set(
    bases["Matricula"]["ID_ANO_ENTIDADE"]
)

ids_docente = set(
    bases["Docente"]["ID_ANO_ENTIDADE"]
)


matricula_sem_escola = (
    ids_matricula - ids_escola
)

docente_sem_escola = (
    ids_docente - ids_escola
)


registrar_teste(
    "Matricula",
    "Relacionamentos",
    "Entidades sem correspondência em Escola",
    0,
    len(matricula_sem_escola),
    len(matricula_sem_escola) == 0
)

registrar_teste(
    "Docente",
    "Relacionamentos",
    "Entidades sem correspondência em Escola",
    0,
    len(docente_sem_escola),
    len(docente_sem_escola) == 0
)


print(
    f"Matrícula sem Escola: "
    f"{len(matricula_sem_escola):,}"
)

print(
    f"Docente sem Escola:   "
    f"{len(docente_sem_escola):,}"
)


# Também registramos a diferença conhecida entre Matrícula e Docente.
# Essa informação não representa erro, pois já foi investigada na M3.

docente_sem_matricula = (
    ids_docente - ids_matricula
)

matricula_sem_docente = (
    ids_matricula - ids_docente
)

print(
    f"Docente sem Matrícula: "
    f"{len(docente_sem_matricula):,}"
)

print(
    f"Matrícula sem Docente: "
    f"{len(matricula_sem_docente):,}"
)


# =============================================================================
# RELATÓRIO CONSOLIDADO
# =============================================================================

df_resultados = pd.DataFrame(resultados)

arquivo_relatorio = (
    EXPLORACAO_DIR /
    "validacao_bases_tratadas_2025.csv"
)

df_resultados.to_csv(
    arquivo_relatorio,
    index=False,
    encoding="utf-8-sig"
)


# =============================================================================
# STATUS FINAL
# =============================================================================

quantidade_revisar = (
    df_resultados["status"] == "REVISAR"
).sum()


print("\n" + "=" * 80)
print("RESUMO FINAL")
print("=" * 80)

print(
    df_resultados["status"]
    .value_counts()
    .to_string()
)

print(f"\nTestes com status REVISAR: {quantidade_revisar}")


if quantidade_revisar == 0:

    print("\nSTATUS FINAL: OK")

else:

    print("\nSTATUS FINAL: REVISAR")


print(f"\nRelatório gerado:")
print(arquivo_relatorio)

print("\nValidação final concluída.")