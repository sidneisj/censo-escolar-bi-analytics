import pandas as pd
from pathlib import Path


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
# Este script cria variáveis derivadas utilizadas nas análises e no Tableau.
#
# Princípios adotados:
#
# - preservar todas as variáveis oficiais do INEP;
# - não substituir códigos originais;
# - adicionar descrições amigáveis para variáveis categóricas;
# - criar apenas campos com utilidade analítica clara;
# - manter as regras de derivação explícitas e reproduzíveis.
#
# Entrada:
#     bases tratadas geradas na issue #24
#
# Saída:
#     bases enriquecidas com as variáveis derivadas.


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


ARQUIVOS = {
    "Escola": {
        "entrada": PROCESSED_DIR / "escola_2025_tratada.csv",
        "saida": PROCESSED_DIR / "escola_2025_derivada.csv",
    },

    "Matricula": {
        "entrada": PROCESSED_DIR / "matricula_2025_tratada.csv",
        "saida": PROCESSED_DIR / "matricula_2025_derivada.csv",
    },

    "Docente": {
        "entrada": PROCESSED_DIR / "docente_2025_tratada.csv",
        "saida": PROCESSED_DIR / "docente_2025_derivada.csv",
    },
}


# =============================================================================
# MAPEAMENTOS OFICIAIS DO INEP
# =============================================================================
# Os rótulos abaixo seguem as categorias presentes no dicionário de dados
# oficial do Censo Escolar.
#
# Os códigos originais permanecem nas bases.
# As novas colunas DS_* apenas fornecem descrições amigáveis.


MAPA_DEPENDENCIA = {
    1: "Federal",
    2: "Estadual",
    3: "Municipal",
    4: "Privada",
}


MAPA_LOCALIZACAO = {
    1: "Urbana",
    2: "Rural",
}


MAPA_SITUACAO_FUNCIONAMENTO = {
    1: "Em Atividade",
    2: "Paralisada",
    3: "Extinta (ano do Censo)",
    4: "Extinta em Anos Anteriores",
}


# =============================================================================
# FUNÇÃO PARA CRIAÇÃO DA CHAVE HISTÓRICA
# =============================================================================

def criar_id_ano_entidade(df):
    """
    Cria uma chave textual única utilizando:

        NU_ANO_CENSO + CO_ENTIDADE

    Exemplo:

        2025 + 43145833
        ->
        2025_43145833

    Essa chave permite distinguir a mesma escola em diferentes anos do
    Censo Escolar e será útil na futura consolidação histórica.
    """

    ano = (
        pd.to_numeric(
            df["NU_ANO_CENSO"],
            errors="coerce"
        )
        .astype("Int64")
        .astype("string")
    )

    entidade = (
        df["CO_ENTIDADE"]
        .astype("string")
        .str.zfill(8)
    )

    return ano + "_" + entidade


# =============================================================================
# FUNÇÃO DE VALIDAÇÃO DE MAPEAMENTO
# =============================================================================

def validar_mapeamento(df, coluna, mapa):
    """
    Verifica se todos os códigos preenchidos encontrados na base estão
    previstos no respectivo mapeamento.

    Caso apareça um código novo ou inesperado, o processo é interrompido.

    Isso evita gerar descrições nulas silenciosamente quando uma categoria
    oficial mudar em anos futuros.
    """

    valores_encontrados = set(
        pd.to_numeric(
            df[coluna],
            errors="coerce"
        )
        .dropna()
        .astype(int)
        .unique()
    )

    valores_previstos = set(mapa.keys())

    valores_desconhecidos = (
        valores_encontrados - valores_previstos
    )

    if valores_desconhecidos:

        raise ValueError(
            f"Códigos não mapeados encontrados em {coluna}: "
            f"{sorted(valores_desconhecidos)}"
        )


# =============================================================================
# PROCESSAMENTO
# =============================================================================

print("=" * 80)
print("CRIAÇÃO DE VARIÁVEIS DERIVADAS")
print("=" * 80)


for tabela, arquivos in ARQUIVOS.items():

    print(f"\n{'=' * 80}")
    print(tabela.upper())
    print("=" * 80)


    # =========================================================================
    # LEITURA
    # =========================================================================

    df = pd.read_csv(
        arquivos["entrada"],
        encoding="utf-8-sig",
        dtype={
            "CO_ENTIDADE": "string"
        },
        low_memory=False
    )


    total_antes = len(df)


    # =========================================================================
    # CHAVE HISTÓRICA
    # =========================================================================
    # Essa variável é criada nas três tabelas para facilitar relacionamentos
    # e validações após a futura consolidação dos anos.

    df["ID_ANO_ENTIDADE"] = criar_id_ano_entidade(df)

    print("\nVariável criada:")
    print("- ID_ANO_ENTIDADE")


    # =========================================================================
    # VARIÁVEIS ESPECÍFICAS DA TABELA ESCOLA
    # =========================================================================

    if tabela == "Escola":


        # ---------------------------------------------------------------------
        # DEPENDÊNCIA ADMINISTRATIVA
        # ---------------------------------------------------------------------

        validar_mapeamento(
            df,
            "TP_DEPENDENCIA",
            MAPA_DEPENDENCIA
        )

        df["DS_DEPENDENCIA"] = (
            df["TP_DEPENDENCIA"]
            .map(MAPA_DEPENDENCIA)
            .astype("string")
        )


        # ---------------------------------------------------------------------
        # REDE PÚBLICA / PRIVADA
        # ---------------------------------------------------------------------
        # Segundo a classificação utilizada no projeto:
        #
        # 1 - Federal   -> Pública
        # 2 - Estadual  -> Pública
        # 3 - Municipal -> Pública
        # 4 - Privada   -> Privada
        #
        # Essa é uma variável analítica derivada, e não um campo original
        # fornecido pelo INEP.

        MAPA_REDE = {
            1: "Pública",
            2: "Pública",
            3: "Pública",
            4: "Privada",
        }

        df["DS_REDE"] = (
            df["TP_DEPENDENCIA"]
            .map(MAPA_REDE)
            .astype("string")
        )


        # ---------------------------------------------------------------------
        # LOCALIZAÇÃO
        # ---------------------------------------------------------------------

        validar_mapeamento(
            df,
            "TP_LOCALIZACAO",
            MAPA_LOCALIZACAO
        )

        df["DS_LOCALIZACAO"] = (
            df["TP_LOCALIZACAO"]
            .map(MAPA_LOCALIZACAO)
            .astype("string")
        )


        # ---------------------------------------------------------------------
        # SITUAÇÃO DE FUNCIONAMENTO
        # ---------------------------------------------------------------------

        validar_mapeamento(
            df,
            "TP_SITUACAO_FUNCIONAMENTO",
            MAPA_SITUACAO_FUNCIONAMENTO
        )

        df["DS_SITUACAO_FUNCIONAMENTO"] = (
            df["TP_SITUACAO_FUNCIONAMENTO"]
            .map(MAPA_SITUACAO_FUNCIONAMENTO)
            .astype("string")
        )


        # ---------------------------------------------------------------------
        # INDICADOR DE ESCOLA ATIVA
        # ---------------------------------------------------------------------
        # Facilita cálculos de quantidade de escolas em funcionamento.
        #
        # 1 -> Em atividade
        # 0 -> Demais situações
        #
        # O código oficial TP_SITUACAO_FUNCIONAMENTO continua preservado.

        df["FL_ESCOLA_ATIVA"] = (
            df["TP_SITUACAO_FUNCIONAMENTO"] == 1
        ).astype("Int64")


        print("- DS_DEPENDENCIA")
        print("- DS_REDE")
        print("- DS_LOCALIZACAO")
        print("- DS_SITUACAO_FUNCIONAMENTO")
        print("- FL_ESCOLA_ATIVA")


    # =========================================================================
    # VALIDAÇÃO DA CHAVE DERIVADA
    # =========================================================================

    nulos_id = df["ID_ANO_ENTIDADE"].isna().sum()

    duplicados_id = df["ID_ANO_ENTIDADE"].duplicated().sum()

    print("\n--- Validação da chave derivada ---")

    print(
        f"ID_ANO_ENTIDADE nulo:       "
        f"{nulos_id:,}"
    )

    print(
        f"ID_ANO_ENTIDADE duplicado:  "
        f"{duplicados_id:,}"
    )


    if nulos_id > 0 or duplicados_id > 0:

        raise ValueError(
            f"Problema identificado em ID_ANO_ENTIDADE "
            f"na tabela {tabela}."
        )


    # =========================================================================
    # VALIDAÇÃO DA QUANTIDADE DE REGISTROS
    # =========================================================================
    # A criação de colunas não deve adicionar nem remover linhas.

    total_depois = len(df)

    if total_antes != total_depois:

        raise ValueError(
            f"A quantidade de registros da tabela {tabela} foi alterada."
        )


    # =========================================================================
    # GRAVAÇÃO
    # =========================================================================

    df.to_csv(
        arquivos["saida"],
        index=False,
        encoding="utf-8-sig"
    )


    print("\n--- Resultado ---")

    print(
        f"Registros: "
        f"{total_depois:,}"
    )

    print(
        f"Colunas:   "
        f"{len(df.columns)}"
    )

    print(
        f"Arquivo:   "
        f"{arquivos['saida'].name}"
    )


# =============================================================================
# FINALIZAÇÃO
# =============================================================================

print("\n" + "=" * 80)
print("Criação de variáveis derivadas concluída.")
print("=" * 80)