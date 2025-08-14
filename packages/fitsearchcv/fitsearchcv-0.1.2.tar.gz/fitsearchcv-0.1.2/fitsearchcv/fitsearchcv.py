import warnings
import numpy as np
from sklearn.model_selection import GridSearchCV as _GridSearchCV
from sklearn.model_selection import RandomizedSearchCV as _RandomizedSearchCV


# ---------- helpers ----------

def _looks_like_accuracy(scores, tol=1e-12):
    """Heuristic: scores bounded in [0, 1] (with tiny tolerance) and finite."""
    if scores is None:
        return False
    arr = np.asarray(scores, dtype=float)
    if arr.size == 0:
        return False
    lo, hi = np.nanmin(arr), np.nanmax(arr)
    return np.isfinite(lo) and np.isfinite(hi) and (lo >= -tol) and (hi <= 1 + tol)


def _pick_accuracy_key_from_scoring(scoring):
    """
    From a multi-metric scoring (dict/list/tuple), try to pick an accuracy-like key.
    Returns the key (string) or None if not found.
    """
    if isinstance(scoring, dict):
        # 1) exact name match
        for k in scoring.keys():
            if k and k.lower() in {"accuracy", "acc"}:
                return k
        # 2) name contains 'accuracy' (on key or function repr)
        for k, v in scoring.items():
            name = (str(k) + " " + str(v)).lower()
            if "accuracy" in name or name.strip() == "acc":
                return k
        return None
    if isinstance(scoring, (list, tuple)):
        # lists/tuples of scorer names (strings)
        for k in scoring:
            if isinstance(k, str) and k.lower() in {"accuracy", "acc"}:
                return k
        for k in scoring:
            if isinstance(k, str) and "accuracy" in k.lower():
                return k
        return None
    return None


def _x3_index_from_results(results, metric_suffix=""):
    """
    Compute your x3 = 0.5*(|train - test| + (1 - test)) and return argmin index.
    metric_suffix: "" for single metric, or f"_{metric}" for multi-metric.
    """
    train_key = f"mean_train{metric_suffix}"
    test_key  = f"mean_test{metric_suffix}"

    if train_key not in results or test_key not in results:
        # Fallback: let caller fallback to rank
        raise KeyError(f"Missing keys: {train_key} or {test_key}")

    train = np.asarray(results[train_key], dtype=float)
    test  = np.asarray(results[test_key],  dtype=float)

    # Clamp test to [0,1] to be safe with tiny numeric drift
    test_clamped = np.clip(test, 0.0, 1.0)

    gap = np.abs(train - test_clamped)         # x1
    x2  = 1.0 - test_clamped                   # x2
    x3  = 0.5 * (gap + x2)                     # x3

    x3 = np.where(np.isfinite(x3), x3, np.inf)
    # If everything is inf (degenerate), argmin would error; guard it:
    if not np.isfinite(x3).any():
        raise ValueError("All x3 values are non-finite.")
    return int(np.nanargmin(x3))


# ---------- subclasses ----------

class GridFitCV(_GridSearchCV):
    """
    Drop-in replacement for GridSearchCV:
    - If single-metric and scores are accuracy-like -> select best via x3
    - If multi-metric and refit selects an accuracy-like metric -> use x3 on that metric
    - Otherwise, fallback to sklearn's rank-based selection
    """

    def __init__(self, *args, **kwargs):
        # Ensure train scores exist for x3; if user set False, flip & warn.
        if kwargs.get("return_train_score", True) is False:
            warnings.warn(
                "GridFitCV requires return_train_score=True for x3 selection; overriding to True.",
                RuntimeWarning,
            )
            kwargs["return_train_score"] = True
        else:
            kwargs.setdefault("return_train_score", True)

        scoring = kwargs.get("scoring", None)
        refit = kwargs.get("refit", True)

        # If multi-metric and refit wasn't specified, auto-pick an accuracy-like key
        if (isinstance(scoring, (dict, list, tuple))) and (refit is True or refit is None):
            preferred = _pick_accuracy_key_from_scoring(scoring)
            if preferred is not None:
                kwargs["refit"] = preferred  # satisfy sklearn's multimetric requirement

        super().__init__(*args, **kwargs)

    @staticmethod
    def _select_best_index(refit, refit_metric, results):
        # Case A: single-metric (mean_test_score present)
        single_metric = "mean_test_score" in results and f"rank_test_{refit_metric}" in results
        if single_metric and "mean_train_score" in results and _looks_like_accuracy(results["mean_test_score"]):
            try:
                return _x3_index_from_results(results, metric_suffix="_score".replace("_score", ""))  # -> ""
            except Exception:
                # Fall back to default if x3 cannot be computed robustly
                pass

        # Case B: multi-metric with refit=str (e.g., "accuracy")
        if isinstance(refit, str):
            mt_test_key = f"mean_test_{refit}"
            mt_train_key = f"mean_train_{refit}"
            if (mt_test_key in results) and (mt_train_key in results) and _looks_like_accuracy(results[mt_test_key]):
                try:
                    return _x3_index_from_results(results, metric_suffix=f"_{refit}")
                except Exception:
                    pass  # fallback to default below

        # Fallback: sklearn's default
        return results[f"rank_test_{refit_metric}"].argmin()


class RandomFitCV(_RandomizedSearchCV):
    """
    Drop-in replacement for RandomizedSearchCV:
    - If single-metric and scores are accuracy-like -> select best via x3
    - If multi-metric and refit selects an accuracy-like metric -> use x3 on that metric
    - Otherwise, fallback to sklearn's rank-based selection
    """

    def __init__(self, *args, **kwargs):
        if kwargs.get("return_train_score", True) is False:
            warnings.warn(
                "RandomFitCV requires return_train_score=True for x3 selection; overriding to True.",
                RuntimeWarning,
            )
            kwargs["return_train_score"] = True
        else:
            kwargs.setdefault("return_train_score", True)

        scoring = kwargs.get("scoring", None)
        refit = kwargs.get("refit", True)

        if (isinstance(scoring, (dict, list, tuple))) and (refit is True or refit is None):
            preferred = _pick_accuracy_key_from_scoring(scoring)
            if preferred is not None:
                kwargs["refit"] = preferred

        super().__init__(*args, **kwargs)

    @staticmethod
    def _select_best_index(refit, refit_metric, results):
        # Single-metric path
        single_metric = "mean_test_score" in results and f"rank_test_{refit_metric}" in results
        if single_metric and "mean_train_score" in results and _looks_like_accuracy(results["mean_test_score"]):
            try:
                return _x3_index_from_results(results, metric_suffix="")
            except Exception:
                pass

        # Multi-metric path (refit is the scorer name)
        if isinstance(refit, str):
            mt_test_key = f"mean_test_{refit}"
            mt_train_key = f"mean_train_{refit}"
            if (mt_test_key in results) and (mt_train_key in results) and _looks_like_accuracy(results[mt_test_key]):
                try:
                    return _x3_index_from_results(results, metric_suffix=f"_{refit}")
                except Exception:
                    pass

        # Fallback
        return results[f"rank_test_{refit_metric}"].argmin()
