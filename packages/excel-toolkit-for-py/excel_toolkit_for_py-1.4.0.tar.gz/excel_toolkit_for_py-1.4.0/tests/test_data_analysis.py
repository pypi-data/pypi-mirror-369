"""
Testes para o módulo de análise de dados.
"""

import numpy as np
import pandas as pd
import pytest

from excel_toolkit_for_py.data_analysis import (
    calculate_basic_stats,
    calculate_correlations,
    create_pivot_table,
    detect_outliers,
)


@pytest.fixture
def sample_df():
    """Fixture com DataFrame de exemplo para testes."""
    return pd.DataFrame(
        {
            "A": [1, 2, 3, 4, 5, 100],  # Inclui outlier
            "B": [10, 20, 30, 40, 50, 60],
            "C": ["a", "b", "c", "d", "e", "f"],
            "D": [1.1, 2.2, 3.3, 4.4, 5.5, 6.6],
        }
    )


def test_calculate_basic_stats(sample_df):
    """Testa o cálculo de estatísticas básicas."""
    stats = calculate_basic_stats(sample_df)

    assert "A" in stats
    assert "B" in stats
    assert "D" in stats
    assert "C" not in stats  # Coluna não numérica

    assert stats["A"]["mean"] == pytest.approx(19.17, rel=1e-2)
    assert stats["A"]["median"] == 3.5
    assert stats["A"]["min"] == 1
    assert stats["A"]["max"] == 100


def test_detect_outliers_zscore(sample_df):
    """Testa a detecção de outliers usando z-score."""
    outliers = detect_outliers(sample_df, method="zscore", threshold=2.0)

    assert "A" in outliers
    assert len(outliers["A"]) == 1  # Apenas o valor 100 é outlier
    assert sample_df.loc[outliers["A"][0], "A"] == 100


def test_detect_outliers_iqr(sample_df):
    """Testa a detecção de outliers usando IQR."""
    outliers = detect_outliers(sample_df, method="iqr")

    assert "A" in outliers
    assert len(outliers["A"]) == 1  # Apenas o valor 100 é outlier
    assert sample_df.loc[outliers["A"][0], "A"] == 100


def test_calculate_correlations(sample_df):
    """Testa o cálculo de correlações."""
    corr = calculate_correlations(sample_df)

    assert isinstance(corr, pd.DataFrame)
    assert "A" in corr.index
    assert "B" in corr.index
    assert "D" in corr.index
    assert "C" not in corr.index  # Coluna não numérica

    # Verifica se a matriz é simétrica
    assert corr.loc["A", "B"] == pytest.approx(corr.loc["B", "A"])


def test_create_pivot_table(sample_df):
    """Testa a criação de tabela dinâmica."""
    pivot = create_pivot_table(sample_df, index="C", values=["A", "B"], aggfunc="mean")

    assert isinstance(pivot, pd.DataFrame)
    assert "A" in pivot.columns
    assert "B" in pivot.columns
    assert "a" in pivot.index
    assert "f" in pivot.index

    # Verifica se os valores estão corretos
    assert pivot.loc["a", "A"] == 1
    assert pivot.loc["a", "B"] == 10
