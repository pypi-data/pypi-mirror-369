# fitsearchcv— A smarter `refit` selector for scikit-learn searches

`selector-mean` is a tiny utility that helps reduce **overfitting** and **underfitting** when tuning hyperparameters with scikit-learn’s `GridSearchCV` or `RandomizedSearchCV`.

It provides a single function:

- **`selector_mean(cv_results_, metric=None, use_abs_gap=True, clip01=True)`**  
  A callable you pass to `refit=...` that picks the parameter set balancing **high test performance** and **small train–test gap**.

---

## Why?

Vanilla `GridSearchCV` usually selects the highest mean test score, which can sometimes favor models with high variance.  
`selector_mean` instead minimizes: `0.5 * (|train - test|) + 0.5 * (1 - test)`


