import pandas as pd
from pathlib import Path


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================
# Este script valida as chaves das bases tratadas geradas na issue #24.
#
# Objetivos:
#
# - verificar valores nulos nas chaves;
# - verificar unicidade da combinação NU_ANO_CENSO + CO_ENTIDADE;
# - identificar linhas completamente duplicadas;
# - verificar quantidade de entidades únicas;
# - confirmar o ano de referência presente nas bases;
# - registrar um resumo da validação.
#
# Nenhum registro será removido automaticamente.
#
# Caso sejam encontradas duplicidades, elas deverão ser investigadas antes
# da aplicação de qualquer regra de tratamento.


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
EXPLORACAO_DIR = BASE_DIR / "documentation" / "exploracao"

EXPLORACAO_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# ARQUIVOS DE ENTRADA
# =============================================================================
# Utilizamos as bases tratadas produzidas na issue #24.

ARQUIVOS = {
    "Escola": PROCESSED_DIR / "escola_2025_tratada.csv",
    "Matricula": PROCESSED_DIR / "matricula_2025_tratada.csv",
    "Docente": PROCESSED_DIR / "docente_2025_tratada.csv",
}


# =============================================================================
# CHAVE LÓGICA
# =============================================================================
# Para permitir a futura consolidação de vários anos do Censo Escolar,
# consideramos como chave lógica:
#
#     NU_ANO_CENSO + CO_ENTIDADE
#
# A mesma escola poderá existir em diferentes anos, mas não deverá aparecer
# mais de uma vez na mesma tabela para o mesmo ano, considerando a estrutura
# atual das bases selecionadas.

CHAVE = [
    "NU_ANO_CENSO",
    "CO_ENTIDADE",
]


# =============================================================================
# RESULTADOS
# =============================================================================

resultados = []


print("=" * 80)
print("VALIDAÇÃO DE CHAVES E DUPLICIDADES")
print("=" * 80)


# =============================================================================
# PROCESSAMENTO DAS TABELAS
# =============================================================================

for tabela, arquivo in ARQUIVOS.items():

    print(f"\n{'=' * 80}")
    print(tabela.upper())
    print("=" * 80)


    # -------------------------------------------------------------------------
    # LEITURA
    # -------------------------------------------------------------------------
    # CO_ENTIDADE é lido explicitamente como texto, pois representa um
    # identificador e não uma medida quantitativa.

    df = pd.read_csv(
        arquivo,
        encoding="utf-8-sig",
        dtype={
            "CO_ENTIDADE": "string"
        },
        low_memory=False
    )


    total_registros = len(df)


    # =========================================================================
    # VALIDAÇÃO DE NULOS NAS CHAVES
    # =========================================================================

    nulos_ano = df["NU_ANO_CENSO"].isna().sum()
    nulos_entidade = df["CO_ENTIDADE"].isna().sum()

    registros_chave_nula = (
        df[CHAVE]
        .isna()
        .any(axis=1)
        .sum()
    )


    # =========================================================================
    # ENTIDADES ÚNICAS
    # =========================================================================

    entidades_unicas = df["CO_ENTIDADE"].nunique(dropna=True)


    # =========================================================================
    # DUPLICIDADE DA CHAVE LÓGICA
    # =========================================================================
    # keep=False marca todas as ocorrências envolvidas em uma chave duplicada.

    mascara_chave_duplicada = df.duplicated(
        subset=CHAVE,
        keep=False
    )

    registros_chave_duplicada = mascara_chave_duplicada.sum()

    # Quantidade de combinações de chave que aparecem mais de uma vez.

    chaves_duplicadas = (
        df.loc[mascara_chave_duplicada, CHAVE]
        .drop_duplicates()
        .shape[0]
    )


    # =========================================================================
    # LINHAS COMPLETAMENTE DUPLICADAS
    # =========================================================================

    mascara_linha_duplicada = df.duplicated(
        keep=False
    )

    registros_linha_duplicada = mascara_linha_duplicada.sum()


    # =========================================================================
    # ANOS ENCONTRADOS
    # =========================================================================

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


    # =========================================================================
    # EXIBIÇÃO DOS RESULTADOS
    # =========================================================================

    print(f"\nRegistros:                    {total_registros:,}")
    print(f"Entidades únicas:             {entidades_unicas:,}")

    print("\n--- Chaves ---")

    print(f"NU_ANO_CENSO nulo:            {nulos_ano:,}")
    print(f"CO_ENTIDADE nulo:             {nulos_entidade:,}")
    print(f"Registros com chave nula:     {registros_chave_nula:,}")

    print("\n--- Duplicidades ---")

    print(
        f"Registros em chaves duplicadas: "
        f"{registros_chave_duplicada:,}"
    )

    print(
        f"Chaves distintas duplicadas:    "
        f"{chaves_duplicadas:,}"
    )

    print(
        f"Linhas totalmente duplicadas:   "
        f"{registros_linha_duplicada:,}"
    )

    print(f"\nAno(s) encontrado(s):          {anos}")


    # =========================================================================
    # EXPORTAÇÃO DE DUPLICIDADES
    # =========================================================================
    # Caso alguma chave duplicada seja encontrada, os registros são exportados
    # para investigação.
    #
    # Nenhuma exclusão é realizada neste script.

    if registros_chave_duplicada > 0:

        arquivo_duplicados = (
            EXPLORACAO_DIR /
            f"{tabela.lower()}_2025_chaves_duplicadas.csv"
        )

        (
            df.loc[mascara_chave_duplicada]
            .sort_values(CHAVE)
            .to_csv(
                arquivo_duplicados,
                index=False,
                encoding="utf-8-sig"
            )
        )

        print(
            f"\nATENÇÃO: duplicidades exportadas para "
            f"{arquivo_duplicados.name}"
        )


    # =========================================================================
    # RESULTADO DA VALIDAÇÃO
    # =========================================================================

    valido = (
        registros_chave_nula == 0
        and registros_chave_duplicada == 0
        and registros_linha_duplicada == 0
    )

    status = "OK" if valido else "REVISAR"

    print(f"\nStatus da validação:           {status}")


    # =========================================================================
    # REGISTRO DO RESUMO
    # =========================================================================

    resultados.append({
        "tabela": tabela,
        "total_registros": total_registros,
        "entidades_unicas": entidades_unicas,
        "anos_encontrados": ", ".join(map(str, anos)),
        "nulos_nu_ano_censo": nulos_ano,
        "nulos_co_entidade": nulos_entidade,
        "registros_chave_nula": registros_chave_nula,
        "registros_chave_duplicada": registros_chave_duplicada,
        "chaves_distintas_duplicadas": chaves_duplicadas,
        "registros_linha_duplicada": registros_linha_duplicada,
        "status": status,
    })


# =============================================================================
# GERAÇÃO DO RELATÓRIO
# =============================================================================

df_resultados = pd.DataFrame(resultados)

arquivo_saida = (
    EXPLORACAO_DIR /
    "validacao_chaves_duplicidades_2025.csv"
)

df_resultados.to_csv(
    arquivo_saida,
    index=False,
    encoding="utf-8-sig"
)


# =============================================================================
# RESUMO FINAL
# =============================================================================

print("\n" + "=" * 80)
print("RESUMO")
print("=" * 80)

print(
    df_resultados[
        [
            "tabela",
            "total_registros",
            "entidades_unicas",
            "registros_chave_nula",
            "registros_chave_duplicada",
            "registros_linha_duplicada",
            "status",
        ]
    ].to_string(index=False)
)

print(f"\nRelatório gerado:")
print(arquivo_saida)

print("\nValidação concluída.")