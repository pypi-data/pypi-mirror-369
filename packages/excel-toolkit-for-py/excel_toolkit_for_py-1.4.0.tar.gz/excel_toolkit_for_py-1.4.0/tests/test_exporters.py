"""
Testes para o módulo exporters.py
"""

import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd
import pytest

from excel_toolkit_for_py.exporters import to_html, to_json, to_pdf, to_xml


@pytest.fixture
def sample_data():
    """Fixture com dados de exemplo para os testes"""
    return {
        "dataframe": pd.DataFrame(
            {
                "nome": ["João", "Maria", "Pedro"],
                "idade": [25, 30, 35],
                "cidade": ["São Paulo", "Rio", "Belo Horizonte"],
            }
        ),
        "dict": {
            "pessoa1": {"nome": "João", "idade": 25},
            "pessoa2": {"nome": "Maria", "idade": 30},
        },
        "list": [{"nome": "João", "idade": 25}, {"nome": "Maria", "idade": 30}],
    }


@pytest.fixture
def temp_dir(tmp_path):
    """Fixture que cria um diretório temporário para os arquivos de teste"""
    return tmp_path


def test_to_json_dataframe(sample_data, temp_dir):
    """Testa a exportação de DataFrame para JSON"""
    output_path = temp_dir / "test.json"
    to_json(sample_data["dataframe"], str(output_path))

    assert output_path.exists()
    with open(output_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 3
    assert data[0]["nome"] == "João"


def test_to_json_dict(sample_data, temp_dir):
    """Testa a exportação de dicionário para JSON"""
    output_path = temp_dir / "test.json"
    to_json(sample_data["dict"], str(output_path))

    assert output_path.exists()
    with open(output_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["pessoa1"]["nome"] == "João"


def test_to_xml_dataframe(sample_data, temp_dir):
    """Testa a exportação de DataFrame para XML"""
    output_path = temp_dir / "test.xml"
    to_xml(sample_data["dataframe"], str(output_path))

    assert output_path.exists()
    tree = ET.parse(output_path)
    root = tree.getroot()
    assert len(root) == 3
    assert root[0].find("nome").text == "João"


def test_to_xml_dict(sample_data, temp_dir):
    """Testa a exportação de dicionário para XML"""
    output_path = temp_dir / "test.xml"
    to_xml(sample_data["dict"], str(output_path))

    assert output_path.exists()
    tree = ET.parse(output_path)
    root = tree.getroot()
    assert root.find("pessoa1/nome").text == "João"


def test_to_html_dataframe(sample_data, temp_dir):
    """Testa a exportação de DataFrame para HTML"""
    output_path = temp_dir / "test.html"
    to_html(sample_data["dataframe"], str(output_path))

    assert output_path.exists()
    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "table" in content
    assert "João" in content


def test_to_html_dict(sample_data, temp_dir):
    """Testa a exportação de dicionário para HTML"""
    output_path = temp_dir / "test.html"
    to_html(sample_data["dict"], str(output_path))

    assert output_path.exists()
    with open(output_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "João" in content


def test_to_pdf_dataframe(sample_data, temp_dir):
    """Testa a exportação de DataFrame para PDF"""
    output_path = temp_dir / "test.pdf"
    to_pdf(sample_data["dataframe"], str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_to_pdf_dict(sample_data, temp_dir):
    """Testa a exportação de dicionário para PDF"""
    output_path = temp_dir / "test.pdf"
    to_pdf(sample_data["dict"], str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0
