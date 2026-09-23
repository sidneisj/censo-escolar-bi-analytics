import pandas as pd
from pathlib import Path


# =============================================================================
# CONFIGURAÇÃO DE DIRETÓRIOS
# =============================================================================
# BASE_DIR representa a raiz do projeto.
# A partir dela são definidos os diretórios de dados brutos e processados.

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Garante que a pasta de saída exista antes da geração dos arquivos.
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# ARQUIVOS DE ENTRADA
# =============================================================================
# Mapeamento entre o nome lógico da tabela e o respectivo arquivo oficial
# disponibilizado pelo INEP.
#
# Os arquivos localizados em data/raw/ devem permanecer inalterados durante
# todo o processo de ETL.

ARQUIVOS = {
    "Escola": RAW_DIR / "Tabela_Escola_2025_V2.csv",
    "Matricula": RAW_DIR / "Tabela_Matricula_2025_V2.csv",
    "Docente": RAW_DIR / "Tabela_Docente_2025_V2.csv",
}


# =============================================================================
# VARIÁVEIS UTILIZADAS NO PROJETO
# =============================================================================
# A lista abaixo corresponde às variáveis selecionadas na issue #21.
#
# Nesta etapa do ETL são removidas as colunas que não fazem parte do escopo
# analítico definido para o projeto.
#
# As tabelas Matrícula e Docente permanecem propositalmente enxutas.
# Informações geográficas e administrativas serão obtidas posteriormente
# através do relacionamento com a tabela Escola.

COLUNAS = {

    "Escola": [

        # ---------------------------------------------------------------------
        # Identificação
        # ---------------------------------------------------------------------

        "NU_ANO_CENSO",
        "CO_ENTIDADE",
        "NO_ENTIDADE",

        # ---------------------------------------------------------------------
        # Geografia
        # ---------------------------------------------------------------------

        "CO_REGIAO",
        "NO_REGIAO",

        "CO_UF",
        "SG_UF",
        "NO_UF",

        "CO_MUNICIPIO",
        "NO_MUNICIPIO",

        # ---------------------------------------------------------------------
        # Segmentação e controle
        # ---------------------------------------------------------------------

        "TP_DEPENDENCIA",
        "TP_LOCALIZACAO",
        "TP_SITUACAO_FUNCIONAMENTO",

        # ---------------------------------------------------------------------
        # Infraestrutura
        # ---------------------------------------------------------------------

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
    ],

    "Matricula": [

        # Identificação da entidade e período
        "NU_ANO_CENSO",
        "CO_ENTIDADE",

        # Indicador principal de matrículas
        "QT_MAT_BAS",
    ],

    "Docente": [

        # Identificação da entidade e período
        "NU_ANO_CENSO",
        "CO_ENTIDADE",

        # Indicador principal de docentes
        "QT_DOC_BAS",
    ],
}


# =============================================================================
# FUNÇÃO DE LEITURA DOS CSVs
# =============================================================================

def ler_csv(caminho):
    """
    Realiza a leitura dos arquivos CSV do INEP.

    Os arquivos do Censo Escolar utilizam ponto e vírgula como separador.

    A função tenta inicialmente a codificação UTF-8 com BOM. Caso seja
    identificada incompatibilidade de codificação, utiliza Latin-1 como
    alternativa.

    O parâmetro low_memory=False evita que o Pandas processe o arquivo em
    blocos tentando inferir diferentes tipos para uma mesma coluna.
    """

    try:

        return pd.read_csv(
            caminho,
            sep=";",
            encoding="utf-8-sig",
            low_memory=False
        )

    except UnicodeDecodeError:

        return pd.read_csv(
            caminho,
            sep=";",
            encoding="latin-1",
            low_memory=False
        )


# =============================================================================
# FUNÇÃO DE PADRONIZAÇÃO DE CÓDIGOS
# =============================================================================

def normalizar_codigo(serie, largura):
    """
    Padroniza códigos identificadores como texto.

    Apesar de vários códigos do INEP serem armazenados originalmente como
    números, eles representam identificadores e não medidas quantitativas.

    Por esse motivo, os códigos são convertidos para texto.

    O preenchimento com zeros à esquerda garante que todos os registros
    mantenham uma largura consistente.

    Exemplo:
        código UF 35 -> "35"
        código região 3 -> "3"
        código entidade -> sempre 8 posições
    """

    # Converte inicialmente para número para eliminar possíveis representações
    # como "12345.0" provenientes da leitura do CSV.

    valores = pd.to_numeric(
        serie,
        errors="coerce"
    ).astype("Int64")

    # Converte o resultado para texto e completa zeros à esquerda conforme
    # a largura esperada do identificador.

    return valores.astype("string").str.zfill(largura)


# =============================================================================
# FUNÇÃO PRINCIPAL DE PADRONIZAÇÃO
# =============================================================================

def padronizar(df, tabela):
    """
    Aplica as regras de padronização definidas para cada tabela.

    Nesta issue são realizados apenas:

    - seleção das variáveis utilizadas no projeto;
    - padronização dos tipos de dados;
    - padronização dos identificadores;
    - limpeza básica de campos textuais.

    O tratamento de valores ausentes e códigos especiais será realizado
    posteriormente na issue #24.
    """

    # =========================================================================
    # SELEÇÃO DAS COLUNAS
    # =========================================================================
    # Mantém somente as variáveis aprovadas na issue #21.

    df = df[COLUNAS[tabela]].copy()


    # =========================================================================
    # PADRONIZAÇÃO DO ANO DO CENSO
    # =========================================================================
    # O ano é uma informação numérica inteira.
    #
    # O tipo Int64 do Pandas permite a existência de valores nulos caso
    # algum problema seja identificado no arquivo.

    df["NU_ANO_CENSO"] = pd.to_numeric(
        df["NU_ANO_CENSO"],
        errors="coerce"
    ).astype("Int64")


    # =========================================================================
    # PADRONIZAÇÃO DO CÓDIGO DA ENTIDADE
    # =========================================================================
    # CO_ENTIDADE é a principal chave de relacionamento entre as tabelas.
    #
    # Por se tratar de um identificador, será armazenado como texto com
    # tamanho padronizado de 8 posições.

    df["CO_ENTIDADE"] = normalizar_codigo(
        df["CO_ENTIDADE"],
        8
    )


    # =========================================================================
    # PADRONIZAÇÕES EXCLUSIVAS DA TABELA ESCOLA
    # =========================================================================
    # As informações geográficas e cadastrais ficam centralizadas na tabela
    # Escola, evitando duplicação nas tabelas Matrícula e Docente.

    if tabela == "Escola":


        # ---------------------------------------------------------------------
        # CÓDIGOS GEOGRÁFICOS
        # ---------------------------------------------------------------------
        # Os códigos geográficos são identificadores e, portanto, são
        # armazenados como texto.

        df["CO_REGIAO"] = normalizar_codigo(
            df["CO_REGIAO"],
            1
        )

        df["CO_UF"] = normalizar_codigo(
            df["CO_UF"],
            2
        )

        df["CO_MUNICIPIO"] = normalizar_codigo(
            df["CO_MUNICIPIO"],
            7
        )


        # ---------------------------------------------------------------------
        # CAMPOS TEXTUAIS
        # ---------------------------------------------------------------------
        # Os nomes oficiais são preservados.
        #
        # Nesta etapa apenas espaços em branco no início ou final dos textos
        # são removidos.
        #
        # Não são aplicadas transformações como caixa alta, caixa baixa ou
        # remoção de acentos para não alterar a representação original do INEP.

        colunas_texto = [
            "NO_ENTIDADE",
            "NO_REGIAO",
            "SG_UF",
            "NO_UF",
            "NO_MUNICIPIO",
        ]

        for coluna in colunas_texto:

            df[coluna] = (
                df[coluna]
                .astype("string")
                .str.strip()
            )


    # =========================================================================
    # PADRONIZAÇÃO DAS VARIÁVEIS CATEGÓRICAS
    # =========================================================================
    # Variáveis iniciadas por TP_ representam tipos ou categorias.
    #
    # Variáveis iniciadas por IN_ normalmente representam indicadores
    # categóricos, como 0/1.
    #
    # Os códigos oficiais são preservados e convertidos para inteiros
    # anuláveis.
    #
    # A conversão dos códigos para descrições amigáveis poderá ser realizada
    # posteriormente através de variáveis derivadas ou dimensões auxiliares.

    colunas_categoricas = [
        coluna
        for coluna in df.columns
        if coluna.startswith(("TP_", "IN_"))
    ]

    for coluna in colunas_categoricas:

        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        ).astype("Int64")


    # =========================================================================
    # PADRONIZAÇÃO DAS VARIÁVEIS QUANTITATIVAS
    # =========================================================================
    # Campos iniciados por QT_ representam quantidades.
    #
    # Eles são convertidos para inteiros anuláveis.
    #
    # IMPORTANTE:
    # Nesta etapa códigos especiais, como 88888, ainda são mantidos.
    # Esses códigos serão tratados especificamente na issue #24.

    colunas_quantitativas = [
        coluna
        for coluna in df.columns
        if coluna.startswith("QT_")
    ]

    for coluna in colunas_quantitativas:

        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        ).astype("Int64")


    # Retorna a tabela já reduzida e padronizada.
    return df


# =============================================================================
# EXECUÇÃO DO PROCESSO
# =============================================================================

print("=" * 80)
print("PADRONIZAÇÃO DAS BASES")
print("=" * 80)


# Processa individualmente cada uma das três tabelas selecionadas.
for tabela, arquivo in ARQUIVOS.items():

    print(f"\n{tabela}")


    # =========================================================================
    # LEITURA DA BASE ORIGINAL
    # =========================================================================

    df_original = ler_csv(arquivo)


    # Exibe a dimensão original da tabela antes da seleção de colunas.
    print(
        f"Original:     "
        f"{len(df_original):,} registros / "
        f"{len(df_original.columns)} colunas"
    )


    # =========================================================================
    # APLICAÇÃO DAS REGRAS DE PADRONIZAÇÃO
    # =========================================================================

    df = padronizar(
        df_original,
        tabela
    )


    # =========================================================================
    # DEFINIÇÃO DO ARQUIVO DE SAÍDA
    # =========================================================================
    # Os arquivos tratados são gravados exclusivamente em data/processed/.
    #
    # Dessa forma, os arquivos originais permanecem preservados.

    saida = (
        PROCESSED_DIR /
        f"{tabela.lower()}_2025_padronizada.csv"
    )


    # =========================================================================
    # GRAVAÇÃO DO ARQUIVO PROCESSADO
    # =========================================================================

    df.to_csv(
        saida,
        index=False,
        encoding="utf-8-sig"
    )


    # =========================================================================
    # INFORMAÇÕES PARA VALIDAÇÃO
    # =========================================================================
    # Exibe a quantidade final de registros e colunas.
    #
    # A quantidade de registros deve permanecer igual à base original nesta
    # etapa, pois nenhuma linha está sendo removida.

    print(
        f"Padronizada:  "
        f"{len(df):,} registros / "
        f"{len(df.columns)} colunas"
    )


    # Exibe os tipos de dados resultantes para permitir uma verificação
    # rápida da padronização realizada.

    print("Tipos:")

    for coluna, tipo in df.dtypes.items():

        print(
            f"  {coluna:<35} {tipo}"
        )


    # Informa o nome do arquivo produzido.
    print(f"Arquivo: {saida.name}")


# =============================================================================
# FINALIZAÇÃO
# =============================================================================

print("\nPadronização concluída.")