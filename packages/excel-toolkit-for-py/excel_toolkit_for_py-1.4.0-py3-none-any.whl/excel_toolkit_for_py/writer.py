import pandas as pd


def write_list_to_excel(filename, data, sheet_name="Sheet1"):
    """Cria um arquivo Excel a partir de uma lista de listas."""
    try:
        # Converter a lista em um DataFrame
        df = pd.DataFrame(
            data[1:], columns=data[0]
        )  # Cabeçalho na primeira linha # noqa501

        # Escrever no arquivo Excel
        df.to_excel(
            filename, sheet_name=sheet_name, index=False, engine="openpyxl"
        )  # noqa501
        print(f"✅ Arquivo Excel criado com sucesso: {filename}")
    except Exception as e:
        raise ValueError(f"❌ Erro ao criar o Excel: {str(e)}")


def write_excel(
    dataframe: pd.DataFrame, file_path: str, sheet_name: str = "Sheet1"
) -> None:  # noqa501
    """
    📤 Exporta um DataFrame para um arquivo Excel.

    Args:
        dataframe (pd.DataFrame): DataFrame a ser exportado.
        file_path (str): Caminho de saída do arquivo Excel.
        sheet_name (str): Nome da planilha.
    """
    try:
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
    except Exception as e:
        raise ValueError(
            f"❌ Erro ao exportar o DataFrame para {file_path}: {str(e)}"
        )  # noqa501


def write_csv(dataframe: pd.DataFrame, file_path: str) -> None:
    """
    📤 Exporta um DataFrame para um arquivo CSV.

    Args:
        dataframe (pd.DataFrame): DataFrame a ser exportado.
        file_path (str): Caminho de saída do arquivo CSV.
    """
    try:
        dataframe.to_csv(file_path, index=False)
    except Exception as e:
        raise ValueError(
            f"❌ Erro ao exportar o DataFrame para CSV {file_path}: {str(e)}"
        )  # noqa501
