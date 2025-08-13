"""
Módulo para exportação de dados para diferentes formatos.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd
import weasyprint
from jinja2 import Template


def to_json(
    data: Union[pd.DataFrame, Dict, List], output_path: str, orient: str = "records"
) -> None:
    """
    Exporta dados para um arquivo JSON.

    Args:
        data: DataFrame, dicionário ou lista para exportar
        output_path: Caminho do arquivo de saída
        orient: Orientação do JSON ('records', 'split', 'index', 'columns', 'values', 'table')
    """
    if isinstance(data, pd.DataFrame):
        data.to_json(output_path, orient=orient, indent=4)
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


def to_xml(
    data: Union[pd.DataFrame, Dict, List], output_path: str, root_name: str = "data"
) -> None:
    """
    Exporta dados para um arquivo XML.

    Args:
        data: DataFrame, dicionário ou lista para exportar
        output_path: Caminho do arquivo de saída
        root_name: Nome do elemento raiz do XML
    """

    def dict_to_xml(data_dict: Dict, parent: ET.Element) -> None:
        for key, value in data_dict.items():
            child = ET.SubElement(parent, str(key))
            if isinstance(value, dict):
                dict_to_xml(value, child)
            else:
                child.text = str(value)

    root = ET.Element(root_name)

    if isinstance(data, pd.DataFrame):
        for _, row in data.iterrows():
            record = ET.SubElement(root, "record")
            for col in data.columns:
                child = ET.SubElement(record, str(col))
                child.text = str(row[col])
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                record = ET.SubElement(root, "record")
                dict_to_xml(item, record)
            else:
                child = ET.SubElement(root, "item")
                child.text = str(item)
    elif isinstance(data, dict):
        dict_to_xml(data, root)

    tree = ET.ElementTree(root)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)


def to_html(
    data: Union[pd.DataFrame, Dict, List], output_path: str, template_path: str = None
) -> None:
    """
    Exporta dados para um arquivo HTML.

    Args:
        data: DataFrame, dicionário ou lista para exportar
        output_path: Caminho do arquivo de saída
        template_path: Caminho opcional para um template HTML personalizado
    """
    if template_path and Path(template_path).exists():
        with open(template_path, "r", encoding="utf-8") as f:
            template = Template(f.read())
        html_content = template.render(data=data)
    else:
        if isinstance(data, pd.DataFrame):
            html_content = data.to_html(index=False, classes="table table-striped")
        else:
            html_content = (
                f"<pre>{json.dumps(data, indent=4, ensure_ascii=False)}</pre>"
            )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def to_pdf(
    data: Union[pd.DataFrame, Dict, List], output_path: str, template_path: str = None
) -> None:
    """
    Exporta dados para um arquivo PDF.

    Args:
        data: DataFrame, dicionário ou lista para exportar
        output_path: Caminho do arquivo de saída
        template_path: Caminho opcional para um template HTML personalizado
    """
    # Primeiro, convertemos para HTML
    html_path = str(Path(output_path).with_suffix(".html"))
    to_html(data, html_path, template_path)

    # Depois, convertemos o HTML para PDF
    weasyprint.HTML(filename=html_path).write_pdf(output_path)

    # Removemos o arquivo HTML temporário
    Path(html_path).unlink()
