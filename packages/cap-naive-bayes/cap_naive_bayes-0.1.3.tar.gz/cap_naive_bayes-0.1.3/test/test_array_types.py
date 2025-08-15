import numpy as np
import pandas as pd
import zarr
import cap_anndata
import anndata
import pytest
import scipy.sparse as sp
from tempfile import tempdir
import os

import zarr.storage

from cap_naive_bayes.naive_bayes import NaiveBayesModel


@pytest.fixture
def train_x():
    return np.array([
        [2, 1, 0, 0, 0, 0],
        [2, 0, 1, 0, 0, 0],
        [1, 0, 0, 1, 0, 0],
        [1, 0, 0, 0, 1, 1],
    ])

@pytest.fixture
def train_obs():
    return pd.DataFrame({
        'set1': ['a', 'a', 'a', 'b'],
        'set2': ['c', 'c', 'c', 'd'],
    })

@pytest.fixture
def train_features():
    return pd.Index(['f1', 'f2', 'f3', 'f4', 'f5', 'f6'])

def _test_fit_predict(
    train_x: np.ndarray,
    train_obs: pd.DataFrame,
    train_features: pd.Index,
    chunk: int | None = None,
):
    model = NaiveBayesModel()
    model.fit(train_x, obs=train_obs, features=train_features, chunk=chunk)

    assert model.model_ is not None
    assert isinstance(model.model_, pd.DataFrame)
    assert model.model_.shape == (4, 7)  # 4 labels, 6 features + 1 prior

    x_test = train_x[:, :3]
    feat_test = train_features[:3]

    pred = model.predict(x_test, chunk=chunk, features=feat_test)
    assert isinstance(pred, pd.DataFrame)
    assert pred.shape == (x_test.shape[0], 4)  # 3 samples, 2 labels + 2 conf scores


@pytest.mark.parametrize("chunk", [None, 2, 100])
@pytest.mark.parametrize("dtype", [int, np.float16, np.float32, np.float64])
def test_numpy(train_x, train_obs, train_features, dtype, chunk):
    X = train_x.astype(dtype)
    _test_fit_predict(X, train_obs, train_features, chunk)

@pytest.mark.parametrize("sparse_format", ["csr_matrix", "csc_matrix"])
@pytest.mark.parametrize("chunk", [None, 2, 100])
def test_scipy_sparse(train_x, train_obs, train_features, sparse_format, chunk):
    X = getattr(sp, sparse_format)(train_x)
    _test_fit_predict(X, train_obs, train_features, chunk)


@pytest.mark.parametrize("chunk", [None, 2, 100])
def test_anndata(
    train_x: np.ndarray,
    train_obs: pd.DataFrame,
    train_features: pd.Index,
    chunk: int | None,
):
    adata = anndata.AnnData(X=train_x, obs=train_obs, var=pd.DataFrame(index=train_features))
    _test_fit_predict(adata.X, adata.obs, adata.var.index, chunk)


@pytest.mark.parametrize("sparse", [False, True])
@pytest.mark.parametrize("chunk", [None, 2, 100])
def test_backed_anndata(
    train_x: np.ndarray,
    train_obs: pd.DataFrame,
    train_features: pd.Index,
    chunk: int | None,
    sparse: bool,
):
    x = sp.csr_matrix(train_x) if sparse else train_x
    adata = anndata.AnnData(X=x, obs=train_obs, var=pd.DataFrame(index=train_features))
    file_path = tempdir + "/test_fit_backed_anndata.h5ad"
    adata.write_h5ad(file_path)

    try:
        with cap_anndata.read_h5ad(file_path) as adata:
            adata.read_obs()
            adata.read_var()
            _test_fit_predict(adata.X, adata.obs, adata.var.index, chunk)
    finally:
        os.remove(file_path)


@pytest.mark.parametrize("zarr_chunks", ['auto', [2, 2]])
@pytest.mark.parametrize("chunk", [None, 2, 100])
def test_zarr(
    train_x: np.ndarray,
    train_obs: pd.DataFrame,
    train_features: pd.Index,
    chunk: int | None,
    zarr_chunks: tuple[int, int] | None,
):
    x = zarr.create_array(
        store=zarr.storage.MemoryStore(),
        data=train_x,
        chunks=zarr_chunks,
    )
    
    _test_fit_predict(x, train_obs, train_features, chunk)
