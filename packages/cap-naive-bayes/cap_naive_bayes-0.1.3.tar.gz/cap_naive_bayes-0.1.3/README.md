# CAP-Naive-Bayes

[![PyPI version](https://img.shields.io/pypi/v/cap-naive-bayes)](https://pypi.org/project/cap-naive-bayes/) [![Build Status](https://github.com/cellannotation/cap-naive-bayes/actions/workflows/python-app.yml/badge.svg)](https://github.com/cellannotation/cap-naive-bayes/actions)


A lightweight, extensible implementation of a multinomial Naive Bayes classifier in pure Python. It is designed for **Annotation Transfer** of single-cell data, allowing you to fit and predict on large datasets efficiently using out-of-core chunked processing. 

## Main Features:
- **Out-of-core chunked processing**: Efficiently handle large datasets without loading everything into memory.
- **Support for missing features**: Can handle datasets where some features are missing during prediction.
- **Flexible data formats**: Supports dense NumPy arrays, SciPy sparse matrices, AnnData/HDF5-backed data, Zarr arrays.


# Installation

```commandline
pip install -U cap-naive-bayes
```

# Usage

## Basic Usage
```console
>> from cap_naive_bayes import NaiveBayesModel

>> count_matrix = np.array([
    [2, 1, 0, 0],
    [2, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 1, 1],
])
>> obs = pd.DataFrame({
    'cell_type': ['a', 'a', 'a', 'b'],
})
>> features = pd.Index(['g1', 'g2', 'g3', 'g4'])
>> model = NaiveBayesModel()
>> model.fit(
    X=count_matrix, 
    obs=obs, 
    features=features,
)
>> model  # contains log prior and posterior probabilities
                       g1        g2        g3        g4     prior
labelset  label                                                  
cell_type a     -0.510826 -1.609438 -2.302585 -2.302585 -0.287682
          b     -1.252763 -1.945910 -1.252763 -1.252763 -1.386294

>> pred = model.predict(
    X=count_matrix, 
    labelset="cell_type", 
    features=features,
)
>> pred
  cell_type  cell_type_conf
0         a        0.948776
1         a        0.929726
2         a        0.863014
3         b        0.564414
```

## Chunked Processing

For very large `X` (e.g. Dask, Zarr, HDF5), pass a `chunk` size or let the model infer from `X.chunks`:

```python
# inference of chunk size from .chunks attribute
model.fit(large_zarr_array, obs_df, feature_names, chunk=None)

# explicit chunking
model.predict(X_test, chunk=500)
```

## Feature space allignment

When the feature space of `X` does not match the model's feature space, you can specify the features to use during prediction:

```python
fs_train = pd.Index(['f1', 'f2', 'f3', 'f4', 'f5'])
X_train = ... # matrix with 5 columns
model.fit(X_train, features=fs_train, ...)
fs_test = pd.Index(['f1','f4','f5', 'f6'])
X_test = ... # matrix with 4 columns
pred = model.predict(X_test, features=fs_test) # valid, model will subsample 'f1', 'f4,, 'f5' from model and x_test. 
```

## Multiple labelsets

You can fit the model and make predctions on multiple labelsets by passing a multiple columns in `obs` DataFrame:

```python
obs = pd.DataFrame({
    'cell_type': ['a', 'a', 'a', 'b'],
    'treatment': ['control', 'control', 'treatment', 'treatment']
})
model.fit(X_train, obs=obs, features=fs_train)
pred = model.predict(X_test, features=fs_test)
```

## License & Acknowledgments

This project is released under the BSD 3-Clause License.  
It also incorporates code derived from [scikit-learn](https://scikit-learn.org), which is licensed under the BSD 3‑Clause “New” or “Revised” License.  

- **scikit-learn**  
  Copyright (C) 2007–2024 The scikit-learn developers  
  BSD 3‑Clause License
