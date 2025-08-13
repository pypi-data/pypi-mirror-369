import pandas as pd


def _check_dtype(series, expected_type):
    """
    🎯 Verifica se a série possui o tipo de dado esperado.
    - Aceita floats inteiros como válidos para int.
    - Lida com valores nulos.
    """
    try:
        if expected_type == int:
            return series.dropna().apply(lambda x: float(x).is_integer()).all()
        elif expected_type == float:
            return (
                series.dropna().apply(lambda x: isinstance(x, (float, int))).all()
            )  # noqa501
        elif expected_type == str:
            return series.dropna().apply(lambda x: isinstance(x, str)).all()
        else:
            return (
                series.dropna().apply(lambda x: isinstance(x, expected_type)).all()
            )  # noqa501
    except Exception:
        return False


def validate_excel_schema(file_path, schema, sheet_name=None):
    """
    🛡️ Valida se um arquivo Excel segue o esquema especificado.

    Args:
        file_path (str): Caminho para o arquivo Excel.
        schema (dict): Dicionário com o nome da coluna e o tipo esperado. Ex.: {"Nome": str, "Idade": int} # noqa501
        sheet_name (str ou None): Nome da planilha. Se None, lê a primeira.

    Returns:
        dict: {
            "valid": bool,
            "errors": list (se houver)
        }
    """
    resultado = {"valid": True, "errors": []}

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)

        # ✅ Força leitura da primeira planilha se múltiplas forem retornadas
        if isinstance(df, dict):
            df = list(df.values())[0]

        # 🚨 Verificar se todas as colunas existem e validar tipos
        for coluna, tipo in schema.items():
            if coluna not in df.columns:
                resultado["valid"] = False
                resultado["errors"].append(f"❌ Coluna ausente: '{coluna}'")
            else:
                # 🎯 Validação robusta de tipo
                if not _check_dtype(df[coluna], tipo):
                    resultado["valid"] = False
                    resultado["errors"].append(
                        f"⚠️ Coluna '{coluna}' com tipo inválido. Esperado: {tipo.__name__}"
                    )  # noqa501

    except Exception as e:
        resultado["valid"] = False
        resultado["errors"].append(f"❌ Erro ao validar esquema: {str(e)}")

    return resultado


def validate_excel(file_path, sheet_name=None, **kwargs):
    """
    🛡️ Valida um arquivo Excel.

    Args:
        file_path (str): Caminho para o arquivo Excel.
        sheet_name (str ou None): Nome da planilha. Se None, lê a primeira.
        **kwargs: Argumentos adicionais para pd.read_excel()

    Returns:
        dict: {
            "valid": bool,
            "errors": list (se houver),
            "info": dict (informações sobre o arquivo)
        }
    """
    resultado = {"valid": True, "errors": [], "info": {}}

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)

        # ✅ Força leitura da primeira planilha se múltiplas forem retornadas
        if isinstance(df, dict):
            df = list(df.values())[0]

        # 📊 Coleta informações sobre o arquivo
        resultado["info"] = {
            "linhas": len(df),
            "colunas": len(df.columns),
            "nomes_colunas": list(df.columns),
            "tipos_colunas": {col: str(df[col].dtype) for col in df.columns},
            "valores_nulos": df.isnull().sum().to_dict(),
        }

    except Exception as e:
        resultado["valid"] = False
        resultado["errors"].append(f"❌ Erro ao validar arquivo: {str(e)}")

    return resultado


def validate_csv(file_path, encoding="utf-8", **kwargs):
    """
    🛡️ Valida um arquivo CSV.

    Args:
        file_path (str): Caminho para o arquivo CSV.
        encoding (str): Codificação do arquivo.
        **kwargs: Argumentos adicionais para pd.read_csv()

    Returns:
        dict: {
            "valid": bool,
            "errors": list (se houver),
            "info": dict (informações sobre o arquivo)
        }
    """
    resultado = {"valid": True, "errors": [], "info": {}}

    try:
        df = pd.read_csv(file_path, encoding=encoding, **kwargs)

        # 📊 Coleta informações sobre o arquivo
        resultado["info"] = {
            "linhas": len(df),
            "colunas": len(df.columns),
            "nomes_colunas": list(df.columns),
            "tipos_colunas": {col: str(df[col].dtype) for col in df.columns},
            "valores_nulos": df.isnull().sum().to_dict(),
        }

    except Exception as e:
        resultado["valid"] = False
        resultado["errors"].append(f"❌ Erro ao validar arquivo: {str(e)}")

    return resultado


# 🌟 Exemplo de uso
if __name__ == "__main__":
    # Validação de esquema
    schema = {"Nome": str, "Idade": int, "Salario": float}
    resultado = validate_excel_schema("dados.xlsx", schema)
    if resultado["valid"]:
        print("✅ Validação de esquema bem-sucedida!")
    else:
        print("❌ Validação de esquema falhou:")
        for erro in resultado["errors"]:
            print(" -", erro)

    # Validação geral de Excel
    resultado = validate_excel("dados.xlsx")
    if resultado["valid"]:
        print("\n✅ Validação de Excel bem-sucedida!")
        print("📊 Informações do arquivo:")
        for chave, valor in resultado["info"].items():
            print(f" - {chave}: {valor}")
    else:
        print("\n❌ Validação de Excel falhou:")
        for erro in resultado["errors"]:
            print(" -", erro)

    # Validação de CSV
    resultado = validate_csv("dados.csv")
    if resultado["valid"]:
        print("\n✅ Validação de CSV bem-sucedida!")
        print("📊 Informações do arquivo:")
        for chave, valor in resultado["info"].items():
            print(f" - {chave}: {valor}")
    else:
        print("\n❌ Validação de CSV falhou:")
        for erro in resultado["errors"]:
            print(" -", erro)
