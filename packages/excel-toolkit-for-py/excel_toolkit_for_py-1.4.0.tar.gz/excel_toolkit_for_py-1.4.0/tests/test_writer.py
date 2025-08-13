import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # noqa

import pandas as pd  # noqa
import pytest  # noqa

from excel_toolkit_for_py.writer import (
    write_csv,
    write_excel,  # noqa
    write_list_to_excel,
)


def test_write_excel(tmp_path):
    """Testa a escrita de um arquivo Excel."""
    file_path = tmp_path / "test.xlsx"
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

    write_excel(df, file_path)
    # ✅ Correção: especificar sheet_name para garantir retorno de DataFrame
    df_read = pd.read_excel(file_path, engine="openpyxl", sheet_name="Sheet1")

    pd.testing.assert_frame_equal(df, df_read)


def test_write_csv(tmp_path):
    """Testa a escrita de um arquivo CSV."""
    file_path = tmp_path / "test.csv"
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

    write_csv(df, file_path)
    df_read = pd.read_csv(file_path)

    pd.testing.assert_frame_equal(df, df_read)


def test_write_list_to_excel(tmp_path):
    """Testa a criação de um arquivo Excel a partir de uma lista formatada."""
    file_path = tmp_path / "test_list.xlsx"
    data = [
        ["Nome", "Idade", "Cidade"],
        ["Alice", 25, "São Paulo"],
        ["Carlos", 30, "Rio de Janeiro"],
        ["Mariana", 22, "Belo Horizonte"],
    ]

    write_list_to_excel(file_path, data)
    df_read = pd.read_excel(file_path, engine="openpyxl", sheet_name="Sheet1")

    assert (
        list(df_read.columns) == data[0]
    ), "Os cabeçalhos do Excel não correspondem aos dados de entrada."  # noqa501
    assert df_read.shape == (
        len(data) - 1,
        len(data[0]),
    ), "O formato da planilha não corresponde aos dados de entrada."  # noqa501
