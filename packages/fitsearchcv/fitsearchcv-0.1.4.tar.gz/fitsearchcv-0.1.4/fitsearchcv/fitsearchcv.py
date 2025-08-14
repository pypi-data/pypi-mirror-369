# fitsearchcv/fitsearchcv.py

import warnings
import numpy as np
from sklearn.model_selection import GridSearchCV as _GridSearchCV
from sklearn.model_selection import RandomizedSearchCV as _RandomizedSearchCV

def _looks_like_accuracy(scores, tol=1e-12):
    if scores is None:
        return False
    arr = np.asarray(scores, dtype=float)
    if arr.size == 0:
        return False
    lo, hi = np.nanmin(arr), np.nanmax(arr)
    return np.isfinite(lo) and np.isfinite(hi) and lo >= -tol and hi <= 1 + tol

def _x3_index_from_results(results, metric_suffix=""):
    train = np.asarray(results[f"mean_train{metric_suffix}"], dtype=float)
    test  = np.asarray(results[f"mean_test{metric_suffix}"],  dtype=float)
    test  = np.clip(test, 0.0, 1.0)
    gap = np.abs(train - test)
    x2  = 1.0 - test
    x3  = 0.5 * (gap + x2)
    x3  = np.where(np.isfinite(x3), x3, np.inf)
    return int(np.nanargmin(x3))

class GridFitCV(_GridSearchCV):
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
        if return_train_score is False:
            warnings.warn(
                "GridFitCV needs return_train_score=True for x3; overriding.",
                RuntimeWarning,
            )
            return_train_score = True

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
        single_metric = "mean_test_score" in results and f"rank_test_{refit_metric}" in results
        if single_metric and "mean_train_score" in results and _looks_like_accuracy(results["mean_test_score"]):
            try:
                return _x3_index_from_results(results, metric_suffix="")
            except Exception:
                pass
        return results[f"rank_test_{refit_metric}"].argmin()


class RandomFitCV(_RandomizedSearchCV):
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
                "RandomFitCV needs return_train_score=True for x3; overriding.",
                RuntimeWarning,
            )
            return_train_score = True

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
        return results[f"rank_test_{refit_metric}"].argmin()
