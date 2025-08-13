# 📦 excel_toolkit_for_py/conversions.py

import json

import pandas as pd


def excel_to_json(file_path, sheet_name=None):
    """
    🔄 Converte um arquivo Excel em JSON.

    Args:
        file_path (str): Caminho para o arquivo Excel.
        sheet_name (str ou None): Nome da planilha a ser lida. Se None, lê todas.

    Returns:
        list ou dict: Dados da planilha em formato JSON (lista se única, dict se múltiplas).
    """
    try:
        data = pd.read_excel(file_path, sheet_name=sheet_name)
        if isinstance(data, dict):
            # ✅ Retorna diretamente a lista se houver apenas uma planilha
            return (
                data[list(data.keys())[0]].to_dict(orient="records")
                if len(data) == 1
                else {sheet: df.to_dict(orient="records") for sheet, df in data.items()}
            )
        else:
            return data.to_dict(orient="records")
    except Exception as e:
        raise ValueError(f"❌ Erro ao converter Excel para JSON: {str(e)}")


def json_to_excel(json_data, file_path, sheet_name="Sheet1"):
    """
    🔄 Converte dados JSON em um arquivo Excel.

    Args:
        json_data (list ou dict): Dados JSON a serem convertidos.
        file_path (str): Caminho para salvar o arquivo Excel.
        sheet_name (str): Nome da planilha no arquivo Excel.

    Returns:
        None
    """
    try:
        if isinstance(json_data, dict):
            with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
                for sheet, data in json_data.items():
                    pd.DataFrame(data).to_excel(writer, sheet_name=sheet, index=False)
        else:
            pd.DataFrame(json_data).to_excel(
                file_path, sheet_name=sheet_name, index=False
            )
    except Exception as e:
        raise ValueError(f"❌ Erro ao converter JSON para Excel: {str(e)}")


def excel_to_csv(excel_path, csv_path, sheet_name=0, encoding="utf-8", **kwargs):
    """
    🔄 Converte um arquivo Excel em CSV.

    Args:
        excel_path (str): Caminho para o arquivo Excel.
        csv_path (str): Caminho para salvar o arquivo CSV.
        sheet_name (str ou int): Nome ou índice da planilha a ser convertida.
        encoding (str): Codificação do arquivo CSV.
        **kwargs: Argumentos adicionais para pd.DataFrame.to_csv()

    Returns:
        None
    """
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        df.to_csv(csv_path, encoding=encoding, index=False, **kwargs)
    except Exception as e:
        raise ValueError(f"❌ Erro ao converter Excel para CSV: {str(e)}")


def csv_to_excel(csv_path, excel_path, sheet_name="Sheet1", encoding="utf-8", **kwargs):
    """
    🔄 Converte um arquivo CSV em Excel.

    Args:
        csv_path (str): Caminho para o arquivo CSV.
        excel_path (str): Caminho para salvar o arquivo Excel.
        sheet_name (str): Nome da planilha no arquivo Excel.
        encoding (str): Codificação do arquivo CSV.
        **kwargs: Argumentos adicionais para pd.read_csv()

    Returns:
        None
    """
    try:
        df = pd.read_csv(csv_path, encoding=encoding, **kwargs)
        df.to_excel(excel_path, sheet_name=sheet_name, index=False)
    except Exception as e:
        raise ValueError(f"❌ Erro ao converter CSV para Excel: {str(e)}")


# 🌟 Exemplo de uso
if __name__ == "__main__":
    # Converte Excel -> JSON
    json_data = excel_to_json("exemplo.xlsx")
    print("🔍 JSON extraído:", json.dumps(json_data, indent=2, ensure_ascii=False))

    # Converte JSON -> Excel
    json_to_excel(json_data, "resultado.xlsx")
    print("✅ JSON convertido para Excel com sucesso!")

    # Converte Excel -> CSV
    excel_to_csv("exemplo.xlsx", "resultado.csv")
    print("✅ Excel convertido para CSV com sucesso!")

    # Converte CSV -> Excel
    csv_to_excel("resultado.csv", "resultado_final.xlsx")
    print("✅ CSV convertido para Excel com sucesso!")
