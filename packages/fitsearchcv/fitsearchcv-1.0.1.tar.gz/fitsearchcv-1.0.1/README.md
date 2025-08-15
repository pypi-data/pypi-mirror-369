# **FitSearchCV**— A smarter `refit` selector for scikit-learn searches

`selector-mean` is a tiny utility that helps reduce **overfitting** and **underfitting** when tuning hyperparameters with scikit-learn’s `GridSearchCV` or `RandomizedSearchCV`.

It provides a single function:

- **`selector_mean(cv_results_, metric=None, use_abs_gap=True, clip01=True)`**  
  A callable you pass to `refit=...` that picks the parameter set balancing **high test performance** and **small train–test gap**.

---



## Best Use cases

-Accuracy, Balanced Accuracy

-Precision, Recall, F1, Jaccard similarity

-ROC AUC, PR AUC

-Matthews correlation coefficient (MCC, normalized variant)

---

## Why?

Vanilla `GridSearchCV` usually selects the highest mean test score, which can sometimes favor models with high variance.  
`selector_mean` instead minimizes: `0.5 * (|train - test|) + 0.5 * (1 - test)`  
This prevents both underfittnig and overfitting. 

`|train-test|` is for reducing the gap between train and test accuracy thus decreasing **overfitting**. 

`(1-test)` is for reducing the gap between test accuracy and 1 hence increasing the score thus reducing **underfitting**.

---

## Want to try? 

Just type  
<pre>pip install fitsearhcv</pre>

Github link: [Github](https://github.com/heilswastik/FitSearchCV)

---

## How to Use?

<pre>from fitsearchcv.selectors import selector_mean
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression

lr=LogisticRegression()

param_grid = [
    {'penalty': ['l1'], 'C': [0.1, 1, 10], 'solver': ['liblinear', 'saga']},
    
    {'penalty': ['l2'], 'C': [0.1, 1, 10], 'solver': ['liblinear', 'lbfgs', 'saga', 'sag', 'newton-cg']},
    
    {'penalty': ['elasticnet'], 'C': [0.1, 1, 10], 'solver': ['saga'], 'l1_ratio': [0.0, 0.25, 0.5, 0.75, 1.0]},
    
    {'penalty': [None], 'solver': ['lbfgs', 'sag', 'newton-cg', 'saga']}  
]

grid1=GridSearchCV(estimator=lr,
                   param_grid=param_grid,
                   refit=selector_mean,
                   cv=5, 
                   return_train_score=True,
                   n_jobs=-1)</pre>