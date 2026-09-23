import pandas as pd
from pathlib import Path
from shutil import copyfile


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
# Este script implementa as regras definidas na issue #24.
#
# Entrada:
#     bases padronizadas geradas na issue #23
#
# Saída:
#     bases tratadas utilizadas nas próximas etapas do ETL
#
# Os arquivos originais e as bases padronizadas não são sobrescritos.

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

ARQUIVO_ESCOLA = PROCESSED_DIR / "escola_2025_padronizada.csv"
ARQUIVO_MATRICULA = PROCESSED_DIR / "matricula_2025_padronizada.csv"
ARQUIVO_DOCENTE = PROCESSED_DIR / "docente_2025_padronizada.csv"

SAIDA_ESCOLA = PROCESSED_DIR / "escola_2025_tratada.csv"
SAIDA_MATRICULA = PROCESSED_DIR / "matricula_2025_tratada.csv"
SAIDA_DOCENTE = PROCESSED_DIR / "docente_2025_tratada.csv"


# =============================================================================
# LEITURA DA TABELA ESCOLA
# =============================================================================
# Os códigos são lidos explicitamente como texto para preservar sua função de
# identificadores e evitar alterações como perda de zeros à esquerda.

df = pd.read_csv(
    ARQUIVO_ESCOLA,
    encoding="utf-8-sig",
    dtype={
        "CO_ENTIDADE": "string",
        "CO_REGIAO": "string",
        "CO_UF": "string",
        "CO_MUNICIPIO": "string",
    },
    low_memory=False
)


# =============================================================================
# VARIÁVEIS DE INFRAESTRUTURA
# =============================================================================

colunas_infraestrutura = [
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


print("=" * 80)
print("TRATAMENTO DE VALORES AUSENTES E ESPECIAIS")
print("=" * 80)


# =============================================================================
# VALIDAÇÃO DOS NULOS DE INFRAESTRUTURA
# =============================================================================
# A análise anterior mostrou que 33.652 escolas apresentam todas as variáveis
# de infraestrutura ausentes.
#
# Esses registros pertencem às situações de funcionamento 2 ou 3.
#
# Portanto, os valores NÃO serão substituídos por zero.
#
# Zero possui significado analítico ("não possui"), enquanto NA representa
# informação não aplicável/não disponível para aquele registro.

possui_algum_nulo = df[colunas_infraestrutura].isna().any(axis=1)
todas_nulas = df[colunas_infraestrutura].isna().all(axis=1)

parcialmente_nulos = possui_algum_nulo & ~todas_nulas

print("\n--- Infraestrutura ---")

print(
    f"Registros com todas as informações ausentes: "
    f"{todas_nulas.sum():,}"
)

print(
    f"Registros parcialmente nulos: "
    f"{parcialmente_nulos.sum():,}"
)


# Caso apareça algum registro parcialmente preenchido, interrompemos o processo.
# Esse cenário exigiria investigação antes de aplicar qualquer tratamento.

if parcialmente_nulos.sum() > 0:

    raise ValueError(
        "Foram encontrados registros com infraestrutura parcialmente nula."
    )


# Verifica se os registros totalmente nulos continuam associados apenas às
# situações de funcionamento identificadas durante a investigação.

situacoes_nulos = set(
    df.loc[
        todas_nulas,
        "TP_SITUACAO_FUNCIONAMENTO"
    ]
    .dropna()
    .astype(int)
    .unique()
)

print(
    f"Situações encontradas nos registros sem infraestrutura: "
    f"{sorted(situacoes_nulos)}"
)

if not situacoes_nulos.issubset({2, 3}):

    raise ValueError(
        "Foram encontrados nulos de infraestrutura em situação inesperada."
    )


# =============================================================================
# CORREÇÃO DOS NOMES GEOGRÁFICOS AUSENTES
# =============================================================================
# Foi identificado um registro com:
#
# - código da Região preenchido;
# - código da UF preenchido;
# - código do Município preenchido;
#
# mas com seus respectivos nomes ausentes.
#
# Em vez de inserir valores manualmente, os nomes são recuperados a partir dos
# demais registros da própria base que possuem o mesmo código.
#
# Isso mantém a transformação reproduzível e evita valores digitados
# diretamente no código.


def criar_mapa_unico(df, coluna_codigo, coluna_nome):
    """
    Cria um mapeamento código -> descrição utilizando a própria base.

    Antes de gerar o mapa, valida se cada código possui apenas uma descrição.
    Caso existam duas descrições diferentes para o mesmo código, o processo é
    interrompido para evitar preenchimento incorreto.
    """

    referencia = (
        df[[coluna_codigo, coluna_nome]]
        .dropna()
        .drop_duplicates()
    )

    quantidade_descricoes = (
        referencia
        .groupby(coluna_codigo)[coluna_nome]
        .nunique()
    )

    ambiguos = quantidade_descricoes[
        quantidade_descricoes > 1
    ]

    if not ambiguos.empty:

        raise ValueError(
            f"Existem códigos com mais de uma descrição em "
            f"{coluna_codigo} / {coluna_nome}"
        )

    return (
        referencia
        .drop_duplicates(subset=[coluna_codigo])
        .set_index(coluna_codigo)[coluna_nome]
    )


print("\n--- Geografia ---")


# -----------------------------------------------------------------------------
# Região
# -----------------------------------------------------------------------------

mapa_regiao = criar_mapa_unico(
    df,
    "CO_REGIAO",
    "NO_REGIAO"
)

df["NO_REGIAO"] = df["NO_REGIAO"].fillna(
    df["CO_REGIAO"].map(mapa_regiao)
)


# -----------------------------------------------------------------------------
# UF - sigla
# -----------------------------------------------------------------------------

mapa_sg_uf = criar_mapa_unico(
    df,
    "CO_UF",
    "SG_UF"
)

df["SG_UF"] = df["SG_UF"].fillna(
    df["CO_UF"].map(mapa_sg_uf)
)


# -----------------------------------------------------------------------------
# UF - nome
# -----------------------------------------------------------------------------

mapa_nome_uf = criar_mapa_unico(
    df,
    "CO_UF",
    "NO_UF"
)

df["NO_UF"] = df["NO_UF"].fillna(
    df["CO_UF"].map(mapa_nome_uf)
)


# -----------------------------------------------------------------------------
# Município
# -----------------------------------------------------------------------------

mapa_municipio = criar_mapa_unico(
    df,
    "CO_MUNICIPIO",
    "NO_MUNICIPIO"
)

df["NO_MUNICIPIO"] = df["NO_MUNICIPIO"].fillna(
    df["CO_MUNICIPIO"].map(mapa_municipio)
)


# =============================================================================
# VALIDAÇÃO APÓS O PREENCHIMENTO GEOGRÁFICO
# =============================================================================

colunas_geograficas = [
    "NO_REGIAO",
    "SG_UF",
    "NO_UF",
    "NO_MUNICIPIO",
]

print("\nValores geográficos ausentes após o tratamento:")

for coluna in colunas_geograficas:

    quantidade = df[coluna].isna().sum()

    print(
        f"{coluna:<25} "
        f"{quantidade:,}"
    )


# =============================================================================
# VALORES ESPECIAIS
# =============================================================================
# Durante a M3 foi identificado que algumas variáveis quantitativas do INEP
# podem utilizar o código 88888 como marcador de valor extremo.
#
# Nas variáveis selecionadas para o projeto em 2025 esse código não ocorre.
#
# Por isso, nenhuma substituição é realizada nesta versão da base.
#
# A verificação é mantida para garantir que o comportamento continue sendo
# conhecido caso os dados sejam atualizados futuramente.

print("\n--- Valores especiais ---")

colunas_quantitativas = [
    coluna
    for coluna in df.columns
    if coluna.startswith("QT_")
]

total_88888 = 0

for coluna in colunas_quantitativas:

    quantidade = (
        pd.to_numeric(df[coluna], errors="coerce") == 88888
    ).sum()

    total_88888 += quantidade

    if quantidade > 0:

        print(
            f"{coluna}: "
            f"{quantidade:,} ocorrência(s) de 88888"
        )

if total_88888 == 0:

    print(
        "Nenhuma ocorrência de 88888 nas variáveis "
        "quantitativas selecionadas."
    )


# =============================================================================
# GERAÇÃO DA BASE ESCOLA TRATADA
# =============================================================================

df.to_csv(
    SAIDA_ESCOLA,
    index=False,
    encoding="utf-8-sig"
)


# =============================================================================
# MATRÍCULA E DOCENTE
# =============================================================================
# A análise mostrou que as variáveis selecionadas dessas duas tabelas não
# possuem valores ausentes nem códigos especiais.
#
# Portanto, nenhum tratamento é necessário.
#
# Para preservar exatamente o conteúdo produzido na etapa anterior, os
# arquivos são apenas copiados para a nova etapa do pipeline.

copyfile(
    ARQUIVO_MATRICULA,
    SAIDA_MATRICULA
)

copyfile(
    ARQUIVO_DOCENTE,
    SAIDA_DOCENTE
)


# =============================================================================
# RESUMO
# =============================================================================

print("\n--- Arquivos gerados ---")

print(SAIDA_ESCOLA.name)
print(SAIDA_MATRICULA.name)
print(SAIDA_DOCENTE.name)

print("\n" + "=" * 80)
print("Tratamento concluído.")
print("=" * 80)