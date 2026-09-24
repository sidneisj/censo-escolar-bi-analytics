import numpy as np
import pandas as pd
from pathlib import Path


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
# Issue #36 — Validar o modelo analítico e os indicadores
#
# Objetivo:
#
# Validar se as regras analíticas definidas na M5 produzem resultados
# consistentes com os valores certificados durante a etapa de ETL (M4).
#
# Esta validação não repete o ETL.
#
# Ela verifica:
#
# 1. KPIs principais;
# 2. contagem de escolas;
# 3. comportamento das principais dimensões;
# 4. consistência das agregações;
# 5. indicadores percentuais de infraestrutura;
# 6. indicador positivo de acessibilidade;
# 7. evolução histórica dos KPIs.
#
# A lógica reproduz em Python as regras que posteriormente serão utilizadas
# no Tableau.


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
EXPLORACAO_DIR = BASE_DIR / "documentation" / "exploracao"

EXPLORACAO_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# ARQUIVOS
# =============================================================================

ARQUIVO_BASE = (
    PROCESSED_DIR /
    "censo_escolar_tableau_2019_2025.csv"
)

ARQUIVO_REFERENCIA = (
    EXPLORACAO_DIR /
    "resumo_base_tableau_2019_2025.csv"
)


ARQUIVO_VALIDACAO = (
    EXPLORACAO_DIR /
    "validacao_modelo_analitico_2019_2025.csv"
)

ARQUIVO_INFRAESTRUTURA = (
    EXPLORACAO_DIR /
    "indicadores_infraestrutura_2019_2025.csv"
)

ARQUIVO_EVOLUCAO = (
    EXPLORACAO_DIR /
    "evolucao_kpis_2019_2025.csv"
)


# =============================================================================
# CAMPOS PRINCIPAIS
# =============================================================================

KPIS = {
    "matriculas": "QT_MAT_BAS",
    "docentes": "QT_DOC_BAS",
    "escolas_ativas": "FL_ESCOLA_ATIVA",
    "salas_utilizadas": "QT_SALAS_UTILIZADAS",
}


DIMENSOES_VALIDACAO = [
    "DS_REDE",
    "DS_DEPENDENCIA",
    "DS_LOCALIZACAO",
    "NO_REGIAO",
]


INDICADORES_INFRAESTRUTURA = [
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


# =============================================================================
# LEITURA
# =============================================================================

def ler_base():
    """
    Lê a base final preparada para o Tableau.
    """

    return pd.read_csv(
        ARQUIVO_BASE,
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


def registrar(
    ano,
    grupo,
    teste,
    esperado,
    observado,
    valido
):
    """
    Registra os testes executados.
    """

    resultados.append({
        "ano": ano,
        "grupo": grupo,
        "teste": teste,
        "esperado": esperado,
        "observado": observado,
        "status": "OK" if valido else "REVISAR",
    })


def iguais(a, b):
    """
    Compara valores numéricos permitindo pequenas diferenças decorrentes
    de representação em ponto flutuante.
    """

    return bool(
        np.isclose(
            float(a),
            float(b),
            equal_nan=True
        )
    )


# =============================================================================
# CARREGAMENTO
# =============================================================================

print("=" * 80)
print("VALIDAÇÃO DO MODELO ANALÍTICO")
print("=" * 80)


if not ARQUIVO_BASE.exists():
    raise FileNotFoundError(
        f"Base Tableau não encontrada: {ARQUIVO_BASE}"
    )


if not ARQUIVO_REFERENCIA.exists():
    raise FileNotFoundError(
        f"Resumo certificado não encontrado: {ARQUIVO_REFERENCIA}"
    )


df = ler_base()


referencia = pd.read_csv(
    ARQUIVO_REFERENCIA,
    encoding="utf-8-sig"
)


print(f"\nRegistros: {len(df):,}")
print(f"Colunas:   {len(df.columns)}")


# =============================================================================
# 1. PERÍODO
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


registrar(
    "Geral",
    "Estrutura",
    "Período histórico",
    str(anos_esperados),
    str(anos_encontrados),
    anos_encontrados == anos_esperados
)


# =============================================================================
# 2. GRANULARIDADE E CHAVES
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


duplicados = (
    df["ID_ANO_ENTIDADE"]
    .duplicated()
    .sum()
)


registrar(
    "Geral",
    "Granularidade",
    "Chaves nulas",
    0,
    chaves_nulas,
    chaves_nulas == 0
)


registrar(
    "Geral",
    "Granularidade",
    "ID_ANO_ENTIDADE duplicada",
    0,
    duplicados,
    duplicados == 0
)


# =============================================================================
# 3. CÁLCULO DOS KPIs SEGUNDO AS REGRAS DA M5
# =============================================================================
# Regras:
#
# Matrículas       = SUM(QT_MAT_BAS)
# Docentes         = SUM(QT_DOC_BAS)
# Escolas Ativas   = SUM(FL_ESCOLA_ATIVA)
# Salas Utilizadas = SUM(QT_SALAS_UTILIZADAS)
#
# Também validamos:
#
# Escolas distintas = COUNTD(CO_ENTIDADE)
# Escola × Ano       = COUNTD(ID_ANO_ENTIDADE)


kpis_calculados = (
    df
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

        registros_escola_ano=(
            "ID_ANO_ENTIDADE",
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


print("\n" + "=" * 80)
print("KPIs ANUAIS")
print("=" * 80)

print(
    kpis_calculados.to_string(
        index=False
    )
)


# =============================================================================
# 4. COMPARAÇÃO COM OS VALORES CERTIFICADOS NA M4
# =============================================================================

print("\n" + "=" * 80)
print("VALIDAÇÃO DOS KPIs CONTRA A M4")
print("=" * 80)


for ano in anos_esperados:

    calculado = kpis_calculados[
        kpis_calculados["NU_ANO_CENSO"] == ano
    ].iloc[0]

    esperado = referencia[
        referencia["NU_ANO_CENSO"] == ano
    ].iloc[0]


    campos = [
        "registros",
        "entidades",
        "escolas_ativas",
        "matriculas",
        "docentes",
        "salas_utilizadas",
    ]


    print(f"\n--- {ano} ---")


    for campo in campos:

        valor_esperado = esperado[campo]
        valor_calculado = calculado[campo]

        valido = iguais(
            valor_esperado,
            valor_calculado
        )

        registrar(
            ano,
            "KPI",
            campo,
            valor_esperado,
            valor_calculado,
            valido
        )


        print(
            f"{campo:<20} "
            f"Esperado: {valor_esperado:,.0f} | "
            f"Calculado: {valor_calculado:,.0f} | "
            f"{'OK' if valido else 'REVISAR'}"
        )


    # -------------------------------------------------------------------------
    # No contexto de um único ano:
    #
    # COUNTD(CO_ENTIDADE)
    # deve ser igual a
    # COUNTD(ID_ANO_ENTIDADE)
    # -------------------------------------------------------------------------

    valido = (
        calculado["entidades"] ==
        calculado["registros_escola_ano"]
    )

    registrar(
        ano,
        "Granularidade",
        "COUNTD escola = COUNTD Escola x Ano em contexto anual",
        calculado["registros_escola_ano"],
        calculado["entidades"],
        valido
    )


# =============================================================================
# 5. VALIDAÇÃO DAS DIMENSÕES
# =============================================================================
# A soma de cada KPI após segmentação por uma dimensão deve retornar ao total
# daquele mesmo ano.
#
# Isso valida, por exemplo:
#
# Pública + Privada = Total
# Federal + Estadual + Municipal + Privada = Total
# Urbana + Rural = Total
# Soma das regiões = Total


print("\n" + "=" * 80)
print("VALIDAÇÃO DAS DIMENSÕES")
print("=" * 80)


for ano in anos_esperados:

    df_ano = df[
        df["NU_ANO_CENSO"] == ano
    ]


    for dimensao in DIMENSOES_VALIDACAO:

        for nome_kpi, coluna in KPIS.items():

            total = pd.to_numeric(
                df_ano[coluna],
                errors="coerce"
            ).sum()


            agrupado = (
                df_ano
                .groupby(
                    dimensao,
                    dropna=False
                )[coluna]
                .sum()
                .sum()
            )


            valido = iguais(
                total,
                agrupado
            )


            registrar(
                ano,
                "Dimensões",
                f"{nome_kpi} por {dimensao}",
                total,
                agrupado,
                valido
            )


print(
    "Validação executada para Rede, Dependência, "
    "Localização e Região."
)


# =============================================================================
# 6. INDICADORES DE INFRAESTRUTURA
# =============================================================================
# Regra definida na M5:
#
# - considerar somente escolas ativas;
# - excluir NULL do denominador;
# - 1 = possui;
# - 0 = não possui.
#
# Percentual:
#
# AVG(indicador 0/1)
#
# Para acessibilidade:
#
# 1 - IN_ACESSIBILIDADE_INEXISTENTE


print("\n" + "=" * 80)
print("INDICADORES DE INFRAESTRUTURA")
print("=" * 80)


resultados_infraestrutura = []


for ano in anos_esperados:

    escolas_ativas = df[
        (df["NU_ANO_CENSO"] == ano)
        &
        (df["FL_ESCOLA_ATIVA"] == 1)
    ].copy()


    total_ativas = len(
        escolas_ativas
    )


    for indicador in INDICADORES_INFRAESTRUTURA:

        serie = pd.to_numeric(
            escolas_ativas[indicador],
            errors="coerce"
        )


        validos = (
            serie.notna().sum()
        )

        nulos = (
            serie.isna().sum()
        )

        quantidade_um = (
            serie == 1
        ).sum()

        quantidade_zero = (
            serie == 0
        ).sum()


        # ---------------------------------------------------------------------
        # Acessibilidade possui lógica inversa.
        # ---------------------------------------------------------------------

        if indicador == "IN_ACESSIBILIDADE_INEXISTENTE":

            com_recurso = quantidade_zero

            percentual = (
                com_recurso / validos
                if validos > 0
                else np.nan
            )

            nome_apresentacao = (
                "Acessibilidade"
            )

        else:

            com_recurso = quantidade_um

            percentual = (
                serie.mean()
                if validos > 0
                else np.nan
            )

            nome_apresentacao = indicador


        resultados_infraestrutura.append({
            "ano": ano,
            "indicador": indicador,
            "nome_apresentacao": nome_apresentacao,
            "escolas_ativas": total_ativas,
            "registros_validos": validos,
            "registros_nulos": nulos,
            "com_recurso": com_recurso,
            "sem_recurso": (
                validos - com_recurso
            ),
            "percentual": percentual,
        })


        # ---------------------------------------------------------------------
        # Validações
        # ---------------------------------------------------------------------

        registrar(
            ano,
            "Infraestrutura",
            f"{indicador}: válidos + nulos = escolas ativas",
            total_ativas,
            validos + nulos,
            (
                validos + nulos ==
                total_ativas
            )
        )


        registrar(
            ano,
            "Infraestrutura",
            f"{indicador}: zero + um = válidos",
            validos,
            quantidade_zero + quantidade_um,
            (
                quantidade_zero + quantidade_um ==
                validos
            )
        )


        percentual_valido = (
            pd.isna(percentual)
            or (
                0 <= percentual <= 1
            )
        )


        registrar(
            ano,
            "Infraestrutura",
            f"{indicador}: percentual entre 0 e 1",
            "0 <= percentual <= 1",
            percentual,
            percentual_valido
        )


df_infraestrutura = pd.DataFrame(
    resultados_infraestrutura
)


# =============================================================================
# 7. VALIDAÇÃO ESPECÍFICA DA ACESSIBILIDADE
# =============================================================================

for ano in anos_esperados:

    dados = df[
        (df["NU_ANO_CENSO"] == ano)
        &
        (df["FL_ESCOLA_ATIVA"] == 1)
    ].copy()


    original = pd.to_numeric(
        dados["IN_ACESSIBILIDADE_INEXISTENTE"],
        errors="coerce"
    )


    indicador_positivo = (
        1 - original
    )


    validos_original = (
        original.notna().sum()
    )

    validos_positivo = (
        indicador_positivo.notna().sum()
    )


    registrar(
        ano,
        "Acessibilidade",
        "Preservação do denominador válido",
        validos_original,
        validos_positivo,
        (
            validos_original ==
            validos_positivo
        )
    )


# =============================================================================
# 8. EVOLUÇÃO HISTÓRICA
# =============================================================================
# Gera uma tabela que poderá ser utilizada posteriormente como referência
# durante a construção das visualizações no Tableau.


df_evolucao = (
    kpis_calculados[
        [
            "NU_ANO_CENSO",
            "matriculas",
            "docentes",
            "escolas_ativas",
            "salas_utilizadas",
        ]
    ]
    .copy()
)


for coluna in [
    "matriculas",
    "docentes",
    "escolas_ativas",
    "salas_utilizadas",
]:

    df_evolucao[
        f"{coluna}_variacao_absoluta"
    ] = (
        df_evolucao[coluna]
        .diff()
    )


    df_evolucao[
        f"{coluna}_variacao_percentual"
    ] = (
        df_evolucao[coluna]
        .pct_change(
            fill_method=None
        )
    )


# =============================================================================
# 9. VALIDAÇÃO DE DUPLA CONTAGEM TEMPORAL
# =============================================================================
# Demonstra que:
#
# COUNTD(CO_ENTIDADE)
#
# não é equivalente à quantidade de registros Escola × Ano quando vários
# anos são considerados.


escolas_distintas_periodo = (
    df["CO_ENTIDADE"]
    .nunique()
)


registros_escola_ano_periodo = (
    df["ID_ANO_ENTIDADE"]
    .nunique()
)


registrar(
    "2019-2025",
    "Temporal",
    "Registros Escola x Ano maiores ou iguais a escolas distintas",
    "ID_ANO_ENTIDADE >= CO_ENTIDADE",
    (
        f"{registros_escola_ano_periodo} >= "
        f"{escolas_distintas_periodo}"
    ),
    (
        registros_escola_ano_periodo
        >= escolas_distintas_periodo
    )
)


# =============================================================================
# 10. VALORES DE CONTROLE DE 2025
# =============================================================================

controle_2025 = kpis_calculados[
    kpis_calculados["NU_ANO_CENSO"] == 2025
].iloc[0]


print("\n" + "=" * 80)
print("VALORES DE CONTROLE — 2025")
print("=" * 80)

print(
    f"Matrículas:       "
    f"{controle_2025['matriculas']:,.0f}"
)

print(
    f"Docentes:         "
    f"{controle_2025['docentes']:,.0f}"
)

print(
    f"Escolas Ativas:   "
    f"{controle_2025['escolas_ativas']:,.0f}"
)

print(
    f"Salas Utilizadas: "
    f"{controle_2025['salas_utilizadas']:,.0f}"
)


# =============================================================================
# 11. EXPORTAÇÃO DOS RESULTADOS
# =============================================================================

df_resultados = pd.DataFrame(
    resultados
)


df_resultados.to_csv(
    ARQUIVO_VALIDACAO,
    index=False,
    encoding="utf-8-sig"
)


df_infraestrutura.to_csv(
    ARQUIVO_INFRAESTRUTURA,
    index=False,
    encoding="utf-8-sig"
)


df_evolucao.to_csv(
    ARQUIVO_EVOLUCAO,
    index=False,
    encoding="utf-8-sig"
)


# =============================================================================
# 12. RESUMO FINAL
# =============================================================================

testes_ok = (
    df_resultados["status"] == "OK"
).sum()


testes_revisar = (
    df_resultados["status"] == "REVISAR"
).sum()


print("\n" + "=" * 80)
print("RESUMO FINAL")
print("=" * 80)

print(
    f"Testes OK:      "
    f"{testes_ok}"
)

print(
    f"Testes REVISAR: "
    f"{testes_revisar}"
)


if testes_revisar == 0:

    print("\nSTATUS FINAL: OK")

else:

    print("\nSTATUS FINAL: REVISAR")


print("\nArquivos gerados:")

print(ARQUIVO_VALIDACAO)
print(ARQUIVO_INFRAESTRUTURA)
print(ARQUIVO_EVOLUCAO)


print("\n" + "=" * 80)
print("Validação do modelo analítico concluída.")
print("=" * 80)