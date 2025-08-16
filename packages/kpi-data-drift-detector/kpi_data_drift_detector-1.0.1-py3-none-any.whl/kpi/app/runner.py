import numpy as np
import pandas as pd

from kpi.app.detector.detector import DataDriftDetector
from kpi.app.profiler.profiler import Profiler


def infer_feature_types(df: pd.DataFrame,
                        max_categories: int = 5):
    numeric, categorical = [], []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].nunique() <= max_categories:
                categorical.append(col)
            else:
                numeric.append(col)
        else:
            categorical.append(col)
    return numeric, categorical

def run_drift_monitoring(
    df_reference: pd.DataFrame,
    df_current:   pd.DataFrame
) -> pd.DataFrame:
    numeric_features, categorical_features = infer_feature_types(df_current, max_categories=5)

    # 2) Профилирование обоих наборов
    profiler = Profiler(numeric_bins=50)
    profile_ref = profiler.profile(df_reference, numeric_features, categorical_features)
    profile_cur = profiler.profile(df_current, numeric_features, categorical_features)

    detector = DataDriftDetector()
    drift_report = detector.detect(profile_ref, profile_cur)

    return drift_report
