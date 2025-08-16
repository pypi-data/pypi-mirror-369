import numpy as np
import pandas as pd
import pytest

from kpi.app.detector.detector import DataDriftDetector
from kpi.app.profiler.profiler import Profiler


# маленькие и большие выборки
def make_df_normal(mu=0, sigma=1, n=500):
    return pd.DataFrame({'v': np.random.normal(mu, sigma, size=n)})

# --- Existing tests ---

def test_no_drift_numeric_small_ks():
    # Test KS-test on small numeric distributions with no drift
    df1 = make_df_normal(n=200)
    df2 = make_df_normal(n=200)
    prof = Profiler(numeric_bins=10)
    pr1 = prof.profile(df1, ['v'], [])
    pr2 = prof.profile(df2, ['v'], [])
    comp = DataDriftDetector(ks_p=0.01)
    report = comp.detect(pr1, pr2)
    assert report.iloc[0]['status'] == 'NO_DRIFT'


def test_drift_numeric_large_wasserstein():
    # Test Wasserstein method on large numeric distributions with drift
    df1 = make_df_normal(mu=0, n=5000)
    df2 = make_df_normal(mu=5, n=5000)
    prof = Profiler(numeric_bins=10)
    pr1 = prof.profile(df1, ['v'], [])
    pr2 = prof.profile(df2, ['v'], [])
    comp = DataDriftDetector(ws_thresh=0.5)
    report = comp.detect(pr1, pr2)
    assert report.iloc[0]['method'] == 'Wasserstein'
    assert report.iloc[0]['status'] == 'DRIFT'


def test_categorical_small_chi2():
    # Test χ²-test on small categorical distributions with drift
    df1 = pd.DataFrame({'c': ['a']*30 + ['b']*20})
    df2 = pd.DataFrame({'c': ['a']*10 + ['b']*40})
    prof = Profiler()
    pr1 = prof.profile(df1, [], ['c'])
    pr2 = prof.profile(df2, [], ['c'])
    comp = DataDriftDetector(chi2_p=0.05)
    report = comp.detect(pr1, pr2)
    assert report.iloc[0]['method'] == 'chi2'
    assert report.iloc[0]['status'] == 'DRIFT'

# --- New tests for missing branches and edge cases ---

def test_binary_numeric_z_test():
    # Test Z-test on binary numeric feature with drift detection
    df1 = pd.DataFrame({'b': [0]*50 + [1]*50})
    df2 = pd.DataFrame({'b': [0]*30 + [1]*70})
    prof = Profiler()
    pr1 = prof.profile(df1, ['b'], [])
    pr2 = prof.profile(df2, ['b'], [])
    comp = DataDriftDetector(zw_p=0.05)
    report = comp.detect(pr1, pr2)
    assert report.iloc[0]['method'] == 'Z-test'
    assert report.iloc[0]['status'] == 'DRIFT'


def test_small_numeric_low_unique_chi2():
    # Test χ²-test on small numeric feature with low unique values
    df1 = pd.DataFrame({'v': [1, 2, 3] * 10})
    df2 = pd.DataFrame({'v': [1, 1, 1, 2, 2, 2, 3, 3, 3] * 3 + [1]})
    prof = Profiler(numeric_bins=3)
    pr1 = prof.profile(df1, ['v'], [])
    pr2 = prof.profile(df2, ['v'], [])
    comp = DataDriftDetector(chi2_p=0.05)
    report = comp.detect(pr1, pr2)
    assert report.iloc[0]['method'] == 'chi2'


def test_large_numeric_low_unique_js():
    # Test JS-divergence on large numeric feature with low unique values
    df1 = pd.DataFrame({'v': [1] * 400 + [2] * 400 + [3] * 400})
    df2 = pd.DataFrame({'v': [1] * 800 + [2] * 200 + [3] * 200})
    prof = Profiler()
    pr1 = prof.profile(df1, ['v'], [])
    pr2 = prof.profile(df2, ['v'], [])
    comp = DataDriftDetector(js_thresh=0.01)
    report = comp.detect(pr1, pr2)
    assert report.iloc[0]['method'] == 'JS'
    assert report.iloc[0]['status'] == 'DRIFT'


def test_large_categorical_js():
    # Test JS-divergence on large categorical feature
    df1 = pd.DataFrame({'c': ['a', 'b', 'c'] * 400})
    df2 = pd.DataFrame({'c': ['a'] * 800 + ['b'] * 200 + ['c'] * 200})
    prof = Profiler()
    pr1 = prof.profile(df1, [], ['c'])
    pr2 = prof.profile(df2, [], ['c'])
    comp = DataDriftDetector(js_thresh=0.01)
    report = comp.detect(pr1, pr2)
    assert report.iloc[0]['method'] == 'JS'
    assert report.iloc[0]['status'] == 'DRIFT'


def test_category_alignment():
    # Test that mismatched categories between ref and cur are aligned without errors
    df1 = pd.DataFrame({'c': ['a', 'b', 'c'] * 10})
    df2 = pd.DataFrame({'c': ['a', 'b'] * 15})
    prof = Profiler()
    pr1 = prof.profile(df1, [], ['c'])
    pr2 = prof.profile(df2, [], ['c'])
    comp = DataDriftDetector()
    report = comp.detect(pr1, pr2)
    assert not report.empty
    assert report.iloc[0]['method'] in ('chi2', 'JS')


def test_constant_numeric_no_drift():
    # Test that a constant numeric feature shows NO_DRIFT
    df = pd.DataFrame({'x': [5] * 100})
    prof = Profiler()
    pr1 = prof.profile(df, ['x'], [])
    pr2 = prof.profile(df, ['x'], [])
    comp = DataDriftDetector()
    report = comp.detect(pr1, pr2)
    assert report.iloc[0]['status'] == 'NO_DRIFT'


def test_report_columns():
    # Test that the report DataFrame has the expected columns
    df1 = make_df_normal(n=100)
    df2 = make_df_normal(n=100)
    prof = Profiler()
    pr1 = prof.profile(df1, ['v'], [])
    pr2 = prof.profile(df2, ['v'], [])
    comp = DataDriftDetector()
    report = comp.detect(pr1, pr2)
    expected_cols = ['feature', 'method', 'score', 'status']
    assert list(report.columns) == expected_cols

# --- Additional tests covering missing branches ---


def test_small_numeric_ks_drift():
    # Test KS-test on small numeric with actual drift detection
    df1 = make_df_normal(mu=0, n=500)
    df2 = make_df_normal(mu=2, n=500)
    prof = Profiler(numeric_bins=10)
    pr1 = prof.profile(df1, ['v'], [])
    pr2 = prof.profile(df2, ['v'], [])
    comp = DataDriftDetector(ks_p=0.05)
    report = comp.detect(pr1, pr2)
    assert report.iloc[0]['method'] == 'KS'
    assert report.iloc[0]['status'] == 'DRIFT'


def test_large_numeric_wasserstein_no_drift():
    # Test Wasserstein on large numeric without drift detection
    df1 = make_df_normal(mu=0, n=5000)
    df2 = make_df_normal(mu=0, n=5000)
    prof = Profiler(numeric_bins=10)
    pr1 = prof.profile(df1, ['v'], [])
    pr2 = prof.profile(df2, ['v'], [])
    comp = DataDriftDetector(ws_thresh=0.1)
    report = comp.detect(pr1, pr2)
    assert report.iloc[0]['method'] == 'Wasserstein'
    assert report.iloc[0]['status'] == 'NO_DRIFT'


def test_large_numeric_low_unique_js_no_drift():
    # Test JS-divergence on large numeric low unique without drift
    df1 = pd.DataFrame({'v': [1]*500 + [2]*500})
    df2 = pd.DataFrame({'v': [1]*500 + [2]*500})
    prof = Profiler(numeric_bins=2)
    pr1 = prof.profile(df1, ['v'], [])
    pr2 = prof.profile(df2, ['v'], [])
    comp = DataDriftDetector(js_thresh=0.05)
    report = comp.detect(pr1, pr2)
    assert report.iloc[0]['method'] == 'JS'
    assert report.iloc[0]['status'] == 'NO_DRIFT'


def test_small_categorical_chi2_no_drift():
    # Test χ²-test on small categorical without drift
    df1 = pd.DataFrame({'c': ['a']*25 + ['b']*25})
    df2 = pd.DataFrame({'c': ['a']*26 + ['b']*24})
    prof = Profiler()
    pr1 = prof.profile(df1, [], ['c'])
    pr2 = prof.profile(df2, [], ['c'])
    comp = DataDriftDetector(chi2_p=0.05)
    report = comp.detect(pr1, pr2)
    assert report.iloc[0]['method'] == 'chi2'
    assert report.iloc[0]['status'] == 'NO_DRIFT'


def test_missing_feature_in_current():
    # Test that missing feature in current profile is skipped
    df1 = pd.DataFrame({'x': [1,2,3]})
    df2 = pd.DataFrame({'y': [1,2,3]})
    prof = Profiler()
    pr1 = prof.profile(df1, ['x'], [])
    pr2 = prof.profile(df2, [], ['y'])
    comp = DataDriftDetector()
    report = comp.detect(pr1, pr2)
    assert report.empty
