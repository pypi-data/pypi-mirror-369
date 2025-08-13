import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 🧪 tests/test_validations.py
import pytest
import pandas as pd
from excel_toolkit_for_py.validations import validate_excel_schema


@pytest.fixture
def sample_excel_file(tmp_path):
    """📁 Cria um arquivo Excel de exemplo para testes."""
    df = pd.DataFrame(
        {
            "Nome": ["Alice", "Bob", "Carlos"],
            "Idade": [30, 25, 22],
            "Salario": [5000.0, 4000.0, 3000.0],
        }
    )
    file_path = tmp_path / "sample.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


# ✅ 🔍 Teste: Validação correta do esquema
def test_validate_excel_schema_valid(sample_excel_file):
    schema = {"Nome": str, "Idade": int, "Salario": float}
    result = validate_excel_schema(sample_excel_file, schema)
    assert result["valid"] is True
    assert result["errors"] == []


# 🚨 ❌ Teste: Coluna ausente
def test_validate_excel_schema_missing_column(sample_excel_file):
    schema = {"Nome": str, "Idade": int, "Departamento": str}
    result = validate_excel_schema(sample_excel_file, schema)
    assert result["valid"] is False
    assert "❌ Coluna ausente: 'Departamento'" in result["errors"]


# 🚨 ⚠️ Teste: Tipo de dado incorreto
def test_validate_excel_schema_invalid_type(sample_excel_file):
    schema = {"Nome": int, "Idade": int, "Salario": float}  # Nome não é int
    result = validate_excel_schema(sample_excel_file, schema)
    assert result["valid"] is False
    assert "⚠️ Coluna 'Nome' com tipo inválido. Esperado: int" in result["errors"]


# 🚨 📝 Teste: Planilha inexistente
def test_validate_excel_schema_invalid_sheet(sample_excel_file):
    schema = {"Nome": str, "Idade": int}
    result = validate_excel_schema(sample_excel_file, schema, sheet_name="Inexistente")
    assert result["valid"] is False
    assert "❌ Erro ao validar esquema" in result["errors"][0]


# 🏃 **Execução dos testes**
if __name__ == "__main__":
    pytest.main(["-v", "tests/test_validations.py"])
