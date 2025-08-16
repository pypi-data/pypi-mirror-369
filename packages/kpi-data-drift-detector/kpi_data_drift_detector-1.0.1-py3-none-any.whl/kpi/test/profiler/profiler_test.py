import numpy as np
import pandas as pd
import pytest

from kpi.app.profiler.profiler import Profiler


@pytest.fixture
def df_numeric():
    return pd.DataFrame({
        'x': np.concatenate([np.arange(50), np.arange(50) + 100])
    })

@pytest.fixture
def df_categorical():
    return pd.DataFrame({
        'cat': ['a']*30 + ['b']*20 + [None]*10
    })

def test_numeric_profile_bins_and_counts(df_numeric):
    p = Profiler(numeric_bins=5)
    prof = p.profile(df_numeric, numeric_features=['x'], categorical_features=[])
    assert 'x' in prof
    info = prof['x']
    # n и n_unique
    assert info['n'] == len(df_numeric)
    assert info['n_unique'] == df_numeric['x'].nunique()
    # число бинов = 5
    assert len(info['histogram']) == 5
    assert len(info['bins']) == 6  # edges = bins + 1
    # raw — numpy array той же длины
    assert isinstance(info['raw'], np.ndarray)
    assert info['raw'].shape[0] == df_numeric['x'].dropna().shape[0]

def test_categorical_profile_frequency(df_categorical):
    p = Profiler()
    prof = p.profile(df_categorical, numeric_features=[], categorical_features=['cat'])
    info = prof['cat']
    # n и n_unique
    assert info['n'] == len(df_categorical)
    assert info['n_unique'] == 3  # 'a','b','NaN'
    # частоты должны суммироваться до n
    total = sum(info['frequency'].values())
    assert total == len(df_categorical)