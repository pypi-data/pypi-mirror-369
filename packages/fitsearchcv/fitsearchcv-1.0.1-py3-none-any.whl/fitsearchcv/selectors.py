import numpy as np

def selector_mean(results, metric=None, use_abs_gap=True, clip01=True):
    if metric is None:
        train_key = "mean_train_score"
        test_key  = "mean_test_score"
    else:
        train_key = f"mean_train_{metric}"
        test_key  = f"mean_test_{metric}"

    if train_key not in results or test_key not in results:
        raise KeyError(f"Missing keys in cv_results_: {train_key}, {test_key}")

    train = np.asarray(results[train_key], dtype=float)
    test  = np.asarray(results[test_key],  dtype=float)

    if clip01:
        test = np.clip(test, 0.0, 1.0)

    gap = np.abs(train - test) if use_abs_gap else (train - test)
    x2  = 1.0 - test
    x3  = 0.5 * (gap + x2)

    x3 = np.where(np.isfinite(x3), x3, np.inf)
    return int(np.nanargmin(x3))
