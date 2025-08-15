import pandas as pd
import os
import tempfile
import numpy as np
import pytest

from cap_naive_bayes.naive_bayes import NaiveBayesModel, PRIOR


def test_init():
    model = NaiveBayesModel()
    assert model.alpha == 1.0
    assert isinstance(model.model_, pd.DataFrame)


def test_dump_load():
    model = NaiveBayesModel()
    index = pd.MultiIndex.from_tuples(
        [
            ('labelset1', 'label1'),
            ('labelset1', 'label2'),
            ('labelset2', 'label1'),
            ('labelset2', 'label2'),
        ]
    )
    data = {
        'feature1': [0.1, 0.2, 0.3, 0.4],
        'feature2': [0.5, 0.6, 0.7, 0.8]
    }
    model.model_ = pd.DataFrame(data=data, index=index)

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "model.pkl")
        model.dump(file_path)
        loaded_model = NaiveBayesModel.load(file_path)
        pd.testing.assert_frame_equal(model.model_, loaded_model.model_)
        
def test_prepare_obs_and_features_dataframe_and_index():
    # Description: This function should convert obs to DataFrame if it's a Series or Index,
    # ensure obs is a DataFrame, convert features to Index if needed, and raise ValueError if types are wrong.
    obs = pd.Series(['a', 'b', 'a'], name='cat')
    features = pd.Index(['f1', 'f2'])
    obs_out, features_out = NaiveBayesModel._prepare_obs_and_features(obs, features)
    assert isinstance(obs_out, pd.DataFrame)
    assert isinstance(features_out, pd.Index)
    assert (features_out == features).all()

def test_prepare_obs_and_features_invalid_obs():
    # Should raise ValueError if obs is not DataFrame, Series, or Index
    obs = ['a', 'b', 'c']
    features = pd.Index(['f1', 'f2'])
    try:
        NaiveBayesModel._prepare_obs_and_features(obs, features)
        assert False, "Should raise ValueError"
    except ValueError:
        pass

def test_prepare_obs_and_features_invalid_features():
    # Should raise ValueError if features is not Index or Series
    obs = pd.DataFrame({'cat': ['a', 'b', 'c']})
    features = ['f1', 'f2']
    try:
        NaiveBayesModel._prepare_obs_and_features(obs, features)
        assert False, "Should raise ValueError"
    except ValueError:
        pass

def test_check_shapes_valid():
    # Should not raise if shapes match
    X = np.zeros((3, 2))
    obs = pd.DataFrame({'cat': ['a', 'b', 'c']})
    var = pd.Index(['f1', 'f2'])
    NaiveBayesModel._check_shapes(X, obs, var)

def test_check_shapes_invalid_rows():
    # Should raise ValueError if X and obs have different number of rows
    X = np.zeros((2, 2))
    obs = pd.DataFrame({'cat': ['a', 'b', 'c']})
    var = pd.Index(['f1', 'f2'])
    try:
        NaiveBayesModel._check_shapes(X, obs, var)
        assert False, "Should raise ValueError"
    except ValueError:
        pass

def test_check_shapes_invalid_columns():
    # Should raise ValueError if X and var have different number of columns
    X = np.zeros((3, 3))
    obs = pd.DataFrame({'cat': ['a', 'b', 'c']})
    var = pd.Index(['f1', 'f2'])
    try:
        NaiveBayesModel._check_shapes(X, obs, var)
        assert False, "Should raise ValueError"
    except ValueError:
        pass

def test_initialize_empty_model_shape_and_index():
    # Should create a DataFrame with MultiIndex and correct shape
    obs = pd.DataFrame({'set1': ['a', 'b', 'a'], 'set2': ['x', 'y', 'x']})
    features = pd.Index(['f1', 'f2'])
    model = NaiveBayesModel._initialize_empty_model(obs, features)
    assert isinstance(model, pd.DataFrame)
    assert model.shape == (len(obs['set1'].unique()) + len(obs['set2'].unique()), len(features))
    assert isinstance(model.index, pd.MultiIndex)
    assert (model.columns == features).all()
    # Check all weights are zero
    assert (model.values == 0).all()

def test_normalize_weights_basic():
    # adapted from https://nlp.stanford.edu/IR-book/html/htmledition/naive-bayes-text-classification-1.html
    index = pd.MultiIndex.from_tuples(
        [
            ('set1', 'a'),
            ('set1', 'b'),
            ('set2', 'c'),
            ('set2', 'd'),

        ],
        names=['labelset', 'label']
    )
    df = pd.DataFrame(
        [
            [5.0, 1.0, 1.0, 1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0, 0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0, 0.0, 1.0, 1.0],
            [5.0, 1.0, 1.0, 1.0, 0.0, 0.0],
        ],
        index=index,
        columns=['f1', 'f2', "f3", 'f4', 'f5', 'f6']
    )
    alpha = 1.0
    normed = df.copy()
    NaiveBayesModel.normalize_weights(normed, alpha)
    
    p_f_a = p_f_d = [3/7, 1/7, 1/7, 1/7, 1/14, 1/14]
    p_f_b = p_f_c = [2/9, 1/9, 1/9, 1/9, 2/9, 2/9]
    df.loc["set1", "a"] = p_f_a
    df.loc["set1", "b"] = p_f_b
    df.loc["set2", "c"] = p_f_c
    df.loc["set2", "d"] = p_f_d

    pd.testing.assert_frame_equal(normed, df)


def test_add_prior():
    obs = pd.DataFrame({
        "set1": ['a', 'a', 'b', 'b'],
        "set2": ['a', 'a', 'a', 'b'],
    })
    df = pd.DataFrame(index=pd.MultiIndex.from_product([["set1", "set2"], ["a", "b"]]))
    expected = df.copy()
    expected["prior"] = [0.5, 0.5, 0.75, 0.25]  # Prior probabilities for each labelset
    NaiveBayesModel._add_prior(df, obs)
    pd.testing.assert_frame_equal(df, expected)

@pytest.mark.parametrize("chunk", [None, 2, 100])
def test_fit_simple(chunk):
    # adopter from https://nlp.stanford.edu/IR-book/html/htmledition/naive-bayes-text-classification-1.html
    
    X = np.array([
        [2, 1, 0, 0, 0, 0],
        [2, 0, 1, 0, 0, 0],
        [1, 0, 0, 1, 0, 0],
        [1, 0, 0, 0, 1, 1],
    ]).astype(np.float64)
    obs = pd.DataFrame({
        'set1': ['a', 'a', 'a', 'b'],
        'set2': ['a', 'a', 'a', 'b'],
    })
    features = pd.Index(['f1', 'f2', 'f3', 'f4', 'f5', 'f6'])
    model = NaiveBayesModel()
    model.fit(X, obs, features, chunk=chunk)
    # Model should have correct index and columns
    assert isinstance(model.model_, pd.DataFrame)
    assert set(model.model_.index.get_level_values(0)) == {'set1', 'set2'}
    assert set(model.model_.index.get_level_values(1)) == {'a', 'b'}
    assert all([f in model.model_.columns for f in features])
    assert model.model_.shape[1] == len(features) + 1 # +1 for prior column
    
    p_f_a = np.log([3/7, 1/7, 1/7, 1/7, 1/14, 1/14])
    p_f_b = np.log([2/9, 1/9, 1/9, 1/9, 2/9, 2/9])
    assert np.allclose(model.model_.loc[('set1', 'a'), features].values, p_f_a)
    assert np.allclose(model.model_.loc[('set1', 'b'), features].values, p_f_b)
    assert np.allclose(model.model_.loc[('set2', 'a'), features].values, p_f_a)
    assert np.allclose(model.model_.loc[('set2', 'b'), features].values, p_f_b)
    assert np.allclose(model.model_.loc[('set1', 'a'), PRIOR], np.log(3/4))
    assert np.allclose(model.model_.loc[('set1', 'b'), PRIOR], np.log(1/4))
    assert np.allclose(model.model_.loc[('set2', 'a'), PRIOR], np.log(3/4))
    assert np.allclose(model.model_.loc[('set2', 'b'), PRIOR], np.log(1/4))


@pytest.mark.parametrize("k", [0.5, 1, 2])
def test_normalize_log_probs(k):
    true_probs = np.array([
        [0.25, 0.25, 0.5],
        [0.1, 0.7, 0.2],
        [1/3, 1/3, 1/3],
        [0.0, 0.0, 1.0],
    ])

    assert all(true_probs.sum(axis=1) == 1)

    log_probs = np.log(true_probs * k)
    normalized_probs = NaiveBayesModel._normalize_log_probs(log_probs)
    assert np.allclose(normalized_probs, true_probs)


@pytest.mark.parametrize("full_var", [True, False])
@pytest.mark.parametrize("labelset", [None, "set1", "set2"])
@pytest.mark.parametrize("chunk", [None, 2, 100])
def test_predict(labelset, chunk, full_var):
    model = NaiveBayesModel()
    model.model_ = pd.DataFrame(
        index=pd.MultiIndex.from_tuples(
            [
                ('set1', 'a'),
                ('set1', 'b'),
                ('set2', 'c'),
                ('set2', 'd'),
            ],
            names=['labelset', 'label']
        ),
        data=np.log([
            [3/7, 1/7, 1/7, 1/7, 1/14, 1/14, 3/4],
            [2/9, 1/9, 1/9, 1/9, 2/9,  2/9,  1/4],
            [3/7, 1/7, 1/7, 1/7, 1/14, 1/14, 3/4],
            [2/9, 1/9, 1/9, 1/9, 2/9,  2/9,  1/4],
        ]),
        columns=['f1', 'f2', 'f3', 'f4', 'f5', 'f6', PRIOR],
    )

    X_test = np.array([
        [3, 0, 0, 0, 1, 1],
        [3, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0],
    ])
    expected = {
        "set1": ['a', 'a', 'b', 'a'],
        "set2": ['c', 'c', 'd', 'c'],
    }
    
    features = None
    if not full_var:
        features = pd.Index(['f1', 'f4', 'f5', 'f6'])
        X_test = X_test[:, model.model_.columns.get_indexer(features)]
    
    predictions = model.predict(X_test, labelset=labelset, chunk=chunk, features=features)

    assert isinstance(predictions, pd.DataFrame)
    assert predictions.shape[0] == X_test.shape[0]
    labelset_to_check = [labelset] if labelset else ["set1", "set2"]

    for ls in labelset_to_check:
        assert ls in predictions.columns
        assert f"{ls}_conf" in predictions.columns
        assert all(predictions[ls].values == expected[ls]), predictions
