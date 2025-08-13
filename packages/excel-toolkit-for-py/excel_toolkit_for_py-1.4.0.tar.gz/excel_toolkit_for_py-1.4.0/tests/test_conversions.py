import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import pandas as pd
from excel_toolkit_for_py.conversions import excel_to_json, json_to_excel


@pytest.fixture
def sample_json_data():
    return [{"Nome": "Alice", "Idade": 30}, {"Nome": "Bob", "Idade": 25}]


@pytest.fixture
def sample_excel_file(tmp_path, sample_json_data):
    file_path = tmp_path / "sample.xlsx"
    df = pd.DataFrame(sample_json_data)
    df.to_excel(file_path, index=False)
    return file_path


# 🔄 ✅ Teste: Excel -> JSON
def test_excel_to_json(sample_excel_file, sample_json_data):
    result = excel_to_json(sample_excel_file)
    assert result == sample_json_data  # ✅ Ajustado para refletir retorno direto


# 🔄 ✅ Teste: JSON -> Excel
def test_json_to_excel(sample_json_data, tmp_path):
    file_path = tmp_path / "output.xlsx"
    json_to_excel(sample_json_data, file_path)
    assert os.path.exists(file_path)

    # ✅ Ajustado para verificar a lista diretamente
    df = pd.read_excel(file_path)
    result = df.to_dict(orient="records")
    assert result == sample_json_data


# 🚨 ❌ Teste: Erro ao converter JSON inválido
def test_json_to_excel_invalid_data(tmp_path):
    file_path = tmp_path / "invalid.xlsx"
    with pytest.raises(ValueError, match="❌ Erro ao converter JSON para Excel"):
        json_to_excel("dados inválidos", file_path)


# 🚨 ❌ Teste: Erro ao converter Excel inválido
def test_excel_to_json_invalid_file():
    with pytest.raises(ValueError, match="❌ Erro ao converter Excel para JSON"):
        excel_to_json("arquivo_inexistente.xlsx")


# 🏃 **Execução dos testes**
if __name__ == "__main__":
    pytest.main(["-v", "tests/test_conversions.py"])
