import pandas as pd


def read_excel(file_path: str, sheet_name: str = None) -> pd.DataFrame:
    """
    📥 Reads an Excel file and returns a DataFrame.

    Args:
        file_path (str): Path to the Excel file.
        sheet_name (str, optional): Sheet name. If None, reads the first sheet.

    Returns:
        pd.DataFrame: Sheet data in DataFrame format.
    """
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")
    except Exception as e:
        raise ValueError(f"❌ Error reading file {file_path}: {str(e)}")


def read_csv(file_path: str) -> pd.DataFrame:
    """
    📥 Reads a CSV file and returns a DataFrame.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: CSV data in DataFrame format.
    """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"❌ Error reading CSV file {file_path}: {str(e)}")


def get_sheet_names(file_path: str) -> list:
    """
    📋 Gets the names of all sheets in an Excel file.

    Args:
        file_path (str): Path to the Excel file.

    Returns:
        list: List of sheet names.
    """
    try:
        xls = pd.ExcelFile(file_path)
        return xls.sheet_names
    except Exception as e:
        raise ValueError(f"❌ Error getting sheet names from {file_path}: {str(e)}")


def get_dict_sheets(file_path: str, sheet_name: str = None) -> dict:
    """
    📋 Gets a dictionary of all sheets in an Excel file.

    Args:
        file_path (str): Path to the Excel file.
        sheet_name (str, optional): Specific sheet name. If None, gets all sheets.

    Returns:
        dict: Dictionary with sheet names as keys and DataFrames as values.
    """
    try:
        dfs = pd.read_excel(file_path, sheet_name=sheet_name)
        return dfs
    except Exception as e:
        raise ValueError(f"❌ Error getting sheets from {file_path}: {str(e)}")
