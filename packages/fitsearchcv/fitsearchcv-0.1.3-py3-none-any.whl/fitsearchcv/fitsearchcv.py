import warnings
import numpy as np
from sklearn.model_selection import GridSearchCV as _GridSearchCV
from sklearn.model_selection import RandomizedSearchCV as _RandomizedSearchCV

# ---------------- helpers ----------------

def _looks_like_accuracy(scores, tol=1e-12):
    if scores is None:
        return False
    arr = np.asarray(scores, dtype=float)
    if arr.size == 0:
        return False
    lo, hi = np.nanmin(arr), np.nanmax(arr)
    return np.isfinite(lo) and np.isfinite(hi) and lo >= -tol and hi <= 1 + tol

def _pick_accuracy_key_from_scoring(scoring):
    if isinstance(scoring, dict):
        for k in scoring.keys():
            if isinstance(k, str) and k.lower() in {"accuracy", "acc"}:
                return k
        for k, v in scoring.items():
            name = (str(k) + " " + str(v)).lower()
            if "accuracy" in name or name.strip() == "acc":
                return k
    elif isinstance(scoring, (list, tuple)):
        for k in scoring:
            if isinstance(k, str) and k.lower() in {"accuracy", "acc"}:
                return k
        for k in scoring:
            if isinstance(k, str) and "accuracy" in k.lower():
                return k
    return None

def _x3_index_from_results(results, metric_suffix=""):
    train_key = f"mean_train{metric_suffix}"
    test_key  = f"mean_test{metric_suffix}"
    train = np.asarray(results[train_key], dtype=float)
    test  = np.asarray(results[test_key],  dtype=float)

    test = np.clip(test, 0.0, 1.0)          # safety for tiny drifts
    gap = np.abs(train - test)              # x1
    x2  = 1.0 - test                        # x2
    x3  = 0.5 * (gap + x2)                  # x3
    x3  = np.where(np.isfinite(x3), x3, np.inf)
    return int(np.nanargmin(x3))


# ---------------- subclasses ----------------

class GridFitCV(_GridSearchCV):
    """
    GridSearchCV that:
      - uses x3 (0.5*(|train-test| + (1-test))) to pick best when metric looks like accuracy
      - auto-picks accuracy key for multi-metric if user didn't set refit
      - otherwise falls back to sklearn's rank-based selection
    """

    def __init__(
        self,
        estimator,
        param_grid,
        *,
        scoring=None,
        n_jobs=None,
        refit=True,
        cv=None,
        verbose=0,
        pre_dispatch="2*n_jobs",
        error_score=np.nan,
        return_train_score=False,
    ):
        # x3 needs train means; if user left default False, flip & warn
        if return_train_score is False:
            warnings.warn(
                "GridFitCV requires return_train_score=True for x3 selection; overriding to True.",
                RuntimeWarning,
            )
            return_train_score = True

        # If multi-metric and refit not specified specifically, choose an accuracy-like key
        if isinstance(scoring, (dict, list, tuple)) and (refit is True or refit is None):
            preferred = _pick_accuracy_key_from_scoring(scoring)
            if preferred is not None:
                refit = preferred

        super().__init__(
            estimator=estimator,
            param_grid=param_grid,
            scoring=scoring,
            n_jobs=n_jobs,
            refit=refit,
            cv=cv,
            verbose=verbose,
            pre_dispatch=pre_dispatch,
            error_score=error_score,
            return_train_score=return_train_score,
        )

    @staticmethod
    def _select_best_index(refit, refit_metric, results):
        # Single-metric path
        single_metric = "mean_test_score" in results and f"rank_test_{refit_metric}" in results
        if single_metric and "mean_train_score" in results and _looks_like_accuracy(results["mean_test_score"]):
            try:
                return _x3_index_from_results(results, metric_suffix="")  # mean_train_score / mean_test_score
            except Exception:
                pass

        # Multi-metric path if refit is a scorer name (e.g., "accuracy")
        if isinstance(refit, str):
            mt_test_key = f"mean_test_{refit}"
            mt_train_key = f"mean_train_{refit}"
            if (mt_test_key in results) and (mt_train_key in results) and _looks_like_accuracy(results[mt_test_key]):
                try:
                    return _x3_index_from_results(results, metric_suffix=f"_{refit}")
                except Exception:
                    pass

        # Fallback to sklearn behavior
        return results[f"rank_test_{refit_metric}"].argmin()


class RandomFitCV(_RandomizedSearchCV):
    """
    RandomizedSearchCV with the same x3-based default selection for accuracy-like metrics.
    """

    def __init__(
        self,
        estimator,
        param_distributions,
        *,
        n_iter=10,
        scoring=None,
        n_jobs=None,
        refit=True,
        cv=None,
        verbose=0,
        pre_dispatch="2*n_jobs",
        random_state=None,
        error_score=np.nan,
        return_train_score=False,
    ):
        if return_train_score is False:
            warnings.warn(
                "RandomFitCV requires return_train_score=True for x3 selection; overriding to True.",
                RuntimeWarning,
            )
            return_train_score = True

        if isinstance(scoring, (dict, list, tuple)) and (refit is True or refit is None):
            preferred = _pick_accuracy_key_from_scoring(scoring)
            if preferred is not None:
                refit = preferred

        super().__init__(
            estimator=estimator,
            param_distributions=param_distributions,
            n_iter=n_iter,
            scoring=scoring,
            n_jobs=n_jobs,
            refit=refit,
            cv=cv,
            verbose=verbose,
            pre_dispatch=pre_dispatch,
            random_state=random_state,
            error_score=error_score,
            return_train_score=return_train_score,
        )

    @staticmethod
    def _select_best_index(refit, refit_metric, results):
        single_metric = "mean_test_score" in results and f"rank_test_{refit_metric}" in results
        if single_metric and "mean_train_score" in results and _looks_like_accuracy(results["mean_test_score"]):
            try:
                return _x3_index_from_results(results, metric_suffix="")
            except Exception:
                pass

        if isinstance(refit, str):
            mt_test_key = f"mean_test_{refit}"
            mt_train_key = f"mean_train_{refit}"
            if (mt_test_key in results) and (mt_train_key in results) and _looks_like_accuracy(results[mt_test_key]):
                try:
                    return _x3_index_from_results(results, metric_suffix=f"_{refit}")
                except Exception:
                    pass

        return results[f"rank_test_{refit_metric}"].argmin()
