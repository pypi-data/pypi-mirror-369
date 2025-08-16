import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, ks_2samp, wasserstein_distance, binomtest


class DataDriftDetector:
    """
    Автоматический выбор метрики и порогов, аналогично Evidently:
      - Константные фичи (n_unique <=1) → NO_DRIFT
      - Бинарные и малые выборки (n_unique == 2 и n_ref < 1000) → Z-тест (p <= zw_p)
      - Малые числовые (n_ref < 1000):
          * n_unique > 5  → KS-тест (p <= ks_p)
          * 2 < n_unique <= 5 → χ²-тест (p <= chi2_p)
      - Большие числовые (n_ref >= 1000):
          * n_unique > 5  → Wasserstein (>= ws_thresh)
          * n_unique <= 5 → JS (>= js_thresh)
      - Категориальные:
          * n_ref < 1000 → χ²-тест
          * n_ref >= 1000 → JS (>= js_thresh)
    """
    def __init__(self,
                 ks_p: float = 0.05,
                 chi2_p: float = 0.05,
                 zw_p: float = 0.05,
                 ws_thresh: float = 0.1,
                 js_thresh: float = 0.1):
        self.ks_p = ks_p
        self.chi2_p = chi2_p
        self.zw_p = zw_p
        self.ws_thresh = ws_thresh
        self.js_thresh = js_thresh

    def compute_js(self, ref_counts, cur_counts):
        # Jensen-Shannon divergence, игнорируем нулевые вероятности
        p = ref_counts / ref_counts.sum()
        q = cur_counts / cur_counts.sum()
        m = 0.5 * (p + q)
        mask_p = p > 0
        mask_q = q > 0
        t1 = np.sum(p[mask_p] * np.log(p[mask_p] / m[mask_p]))
        t2 = np.sum(q[mask_q] * np.log(q[mask_q] / m[mask_q]))
        return 0.5 * (t1 + t2)

    def compare(self, name, ref_pf, cur_pf):
        n_ref = int(ref_pf['n'])
        n_unq = int(ref_pf['n_unique'])
        kind = ref_pf['type']

        # Инициализация
        method = None
        score = 0.0
        drift = False

        # Numeric features
        if kind == 'numeric':
            # Константные
            if n_unq <= 1:
                method = 'constant'
                score = 0.0
                drift = False

            # Бинарные малые
            elif n_unq == 2 and n_ref < 1000:
                raw_ref = ref_pf['raw']
                raw_cur = cur_pf['raw']
                vals_r, cnts_r = np.unique(raw_ref, return_counts=True)
                vals_c, cnts_c = np.unique(raw_cur, return_counts=True)
                cats = sorted(set(vals_r) | set(vals_c))
                freq_r = {c: 0 for c in cats}
                freq_c = {c: 0 for c in cats}
                freq_r.update(dict(zip(vals_r, cnts_r)))
                freq_c.update(dict(zip(vals_c, cnts_c)))
                k = int(freq_c[cats[0]])
                n = int(raw_cur.size)
                p_ref = freq_r[cats[0]] / raw_ref.size
                result = binomtest(k=k, n=n, p=p_ref)
                method = 'Z-test'
                score = result.pvalue
                drift = (score <= self.zw_p)

            # Малые выборки
            elif n_ref < 1000:
                if n_unq > 5:
                    _, p = ks_2samp(ref_pf['raw'], cur_pf['raw'])
                    method = 'KS'
                    score = p
                    drift = (p <= self.ks_p)
                else:
                    ref_counts = np.array(ref_pf['histogram'], dtype=float)
                    cur_counts = np.array(cur_pf['histogram'], dtype=float)
                    _, p, _, _ = chi2_contingency([ref_counts, cur_counts], correction=False)
                    method = 'chi2'
                    score = p
                    drift = (p <= self.chi2_p)

            # Большие выборки
            else:
                if n_unq > 5:
                    score = wasserstein_distance(ref_pf['raw'], cur_pf['raw'])
                    method = 'Wasserstein'
                    drift = (score >= self.ws_thresh)
                else:
                    ref_counts = np.array(ref_pf['histogram'], dtype=float)
                    cur_counts = np.array(cur_pf['histogram'], dtype=float)
                    score = self.compute_js(ref_counts, cur_counts)
                    method = 'JS'
                    drift = (score >= self.js_thresh)

        else:
            # Categorical: синхронизация категорий
            categories = sorted(set(ref_pf['frequency']) | set(cur_pf['frequency']))
            ref_counts = np.array([ref_pf['frequency'].get(c, 0) for c in categories], dtype=float)
            cur_counts = np.array([cur_pf['frequency'].get(c, 0) for c in categories], dtype=float)
            if n_ref < 1000:
                _, p, _, _ = chi2_contingency([ref_counts, cur_counts], correction=False)
                method = 'chi2'
                score = p
                drift = (p <= self.chi2_p)
            else:
                score = self.compute_js(ref_counts, cur_counts)
                method = 'JS'
                drift = (score >= self.js_thresh)

        status = 'DRIFT' if drift else 'NO_DRIFT'
        return {'feature': name, 'method': method, 'score': float(score), 'status': status}

    def detect(self, prof_ref, prof_cur) -> pd.DataFrame:
        records = []
        for feat, ref_pf in prof_ref.items():
            cur_pf = prof_cur.get(feat)
            if cur_pf is None:
                continue
            records.append(self.compare(feat, ref_pf, cur_pf))
        return pd.DataFrame(records)
