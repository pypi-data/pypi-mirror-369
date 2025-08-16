import numpy as np
import pandas as pd

class Profiler:
    """
    Собирает по каждой фиче:
      - кол-во наблюдений (n) и уникальных значений (n_unique),
      - для числовых: гистограмма + сырые данные,
      - для категорий: частоты.
    """
    def __init__(self, numeric_bins: int = 50):
        self.numeric_bins = numeric_bins

    def profile(self,
                df: pd.DataFrame,
                numeric_features: list[str],
                categorical_features: list[str]) -> dict[str, dict]:
        profiles = {}
        n = len(df)
        for col in numeric_features:
            series = df[col].dropna()
            counts, bins = np.histogram(series, bins=self.numeric_bins)
            profiles[col] = {
                'type': 'numeric',
                'n': n,
                'n_unique': int(series.nunique()),
                'histogram': counts.tolist(),
                'bins': bins.tolist(),
                'raw': series.values,
            }
        for col in categorical_features:
            series = df[col].fillna('NaN')
            freqs = series.value_counts().to_dict()
            profiles[col] = {
                'type': 'categorical',
                'n': n,
                'n_unique': int(series.nunique()),
                'frequency': freqs,
            }
        return profiles

