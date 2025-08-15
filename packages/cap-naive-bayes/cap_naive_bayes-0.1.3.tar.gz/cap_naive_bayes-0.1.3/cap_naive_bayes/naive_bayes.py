import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
import scipy.sparse as sp
from os import PathLike
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DEFAULT_ALPHA = 1.0  # Default smoothing parameter for Naive Bayes
PRIOR = "prior"

class NaiveBayesModel:
    def __init__(self, alpha: float = DEFAULT_ALPHA):
        self.alpha = alpha

        # model is dataframe with weights as values
        # index is a multiindex of (labelset, label)
        # columns are the features (var)
        self.model_ = pd.DataFrame()

    def dump(self, path: PathLike):
        """
        Save the model as a dataframe.
        Columns of the dataframe are features + one column for prior probabilities.
        The index is a multiindex of (labelset, label). 
        So, df.loc[(labelset, label), g1] contains log of conditional probability log[P(g1|labelset, label)].
        while df.loc[(labelset, label), 'prior'] contains log of prior probability log[P(labelset, label)].
        """
        logger.debug("Start dump...")
        self.model_.to_parquet(path)
        logger.debug("Dump completed.")

    @classmethod
    def load(cls, path: PathLike):
        logger.debug("Start load...")
        model = pd.read_parquet(path)
        instance = cls()
        instance.model_ = model
        logger.debug("Load completed.")
        return instance
    
    def fit(
        self, 
        X: ArrayLike,
        obs: pd.DataFrame | pd.Series,
        features: pd.Index | pd.Series | None,
        chunk: int | None = None,
    ) -> None:
        """
        Fit the Naive Bayes model to the data.
        Parameters:
        - X: Array-like data for features.
        - obs: Observations (labels) corresponding to the data. Each column should represent a labelset to fit on.
        - features: Index or Series of feature names.
        - chunk: Optional chunk size for processing the data. If None, it will try to infer from X attributes.
        """
        obs, features = self._prepare_obs_and_features(obs, features)
        self._check_shapes(X, obs, features)
        
        if features is None:
            logger.debug("No features provided, using default index.")
            features = pd.Index(range(X.shape[1]))

        if chunk is None:
            logger.debug("Chunk size not provided, try to get from X attributes.")
            chunks = getattr(X, 'chunks', None)
            if chunks is None:
                logger.debug("No chunks attribute found, using full data size.")
                chunk = X.shape[0]
            else:
                logger.debug(f"Chunks found: {chunks}. Using first chunk size.")
                chunk = chunks[0]
        logger.debug(f"Chunk size set to {chunk}.")

        self.model_ = self._initialize_empty_model(obs, features)
        
        
        for from_ in range(0, X.shape[0], chunk):
            to_ = min(from_ + chunk, X.shape[0])
            logger.debug(f"Processing chunk from {from_} to {to_}.")
            X_chunk = X[from_:to_]
            obs_chunk = obs.iloc[from_:to_]

            for col in obs_chunk.columns:
                labels = obs_chunk[col].unique()
                for label in labels:
                    label_mask = (obs_chunk[col] == label).values
                    counts = X_chunk[label_mask]
                    if counts.size > 0:
                        sum_counts = counts.sum(axis=0)
                        if isinstance(sum_counts, np.matrix):
                            logger.debug("Converting sum_counts from matrix to array.")
                            sum_counts = sum_counts.A1

                        self.model_.loc[(col, label)] += sum_counts
        self.normalize_weights(self.model_, self.alpha)
        self._add_prior(self.model_, obs)
        self.model_[:] = np.log(self.model_.values)
        
        logger.debug("Model fitting completed.")

    @staticmethod
    def normalize_weights(model: pd.DataFrame, alpha: float) -> None:
        """ S(l|g) = (S(l|g) + alpha) / (S(l) + alpha * n) """
        logger.debug("Start normalize weights.")
        total = None
        for lbst in model.index.get_level_values("labelset").unique():
            logger.debug(f"Normalizing weights for labelset: {lbst}.")
            df: pd.DataFrame = model.loc[lbst]
            n = df.shape[1]
            total = df.values.sum(axis=1).reshape(-1, 1)

            model.loc[lbst, :] = (df.values + alpha) / (total + alpha * n)
        logger.debug("Weights normalization completed.")
    
    @staticmethod
    def _add_prior(model: pd.DataFrame, obs: pd.DataFrame):
        logger.debug("Start _add_prior...")
        model[PRIOR] = 0.0

        for lbst in obs.columns:
            logger.debug(f"Calculating prior for labelset: {lbst}.")
            vs = obs[lbst].value_counts()
            total = vs.sum()
            for label, count in vs.items():
                model.loc[(lbst, label), PRIOR] = count / total if total > 0 else 0.0
        logger.debug("Prior probabilities added to the model.")

    @staticmethod
    def _initialize_empty_model(obs: pd.DataFrame, features: pd.Index) -> pd.DataFrame:
        logger.debug("Initializing empty model with weights.")
        lbst_to_label = [
            (col, label)
            for col in obs.columns
            for label in obs[col].unique()
        ]
        index = pd.MultiIndex.from_tuples(lbst_to_label, names=['labelset', 'label'])
        weights = np.zeros(shape=(len(index), len(features)), dtype=np.float64)
        empty_model = pd.DataFrame(data=weights, index=index, columns=features)
        logger.debug(f"Empty model initialized with shape {weights.shape}.")
        return empty_model

    @staticmethod
    def _prepare_obs_and_features(
        obs: pd.DataFrame | pd.Series | pd.Index,
        features: pd.Index | pd.Series | None,
    ) -> None:
        logger.debug("Preparing observations and features...")

        if isinstance(obs, (pd.Series, pd.Index)):
            logger.debug("Converting obs to DataFrame.")
            obs = obs.to_frame(name="category")
        
        if not isinstance(obs, pd.DataFrame):
            raise ValueError("obs must be a pandas DataFrame or Series.")
        
        if features is None:
            logger.debug("No features provided.")
        elif isinstance(features, pd.DataFrame):
            features = features.index
        elif isinstance(features, pd.Series):
            features = pd.Index(features)
        
        if not isinstance(features, pd.Index):
            raise ValueError("features must be a pandas Index or Series.")
        return obs, features
    
    @staticmethod
    def _check_shapes(X: ArrayLike, obs: pd.DataFrame, var: pd.Index | None) -> None:
        """
        Check if the shapes of X and obs match.
        """
        if X.shape[0] != obs.shape[0]:
            raise ValueError(f"Shape mismatch: X has {X.shape[0]} rows, obs has {len(obs)} rows.")
        if var is not None and X.shape[1] != len(var):
            raise ValueError(f"Shape mismatch: X has {X.shape[1]} features, var has {len(var)} features.")
        logger.debug("Shapes of X and obs match.")

    def predict(
        self,
        X: ArrayLike,
        labelset: str | None = None,
        features: pd.Index | pd.Series | None = None,
        chunk: int | None = None,
    ):
        if self.model_.empty:
            raise ValueError("Model is empty. Please fit or load the model before predicting.")
        
        n_features = self.model_.shape[1] - 1  # Exclude prior column
        if features is None and X.shape[1] != n_features:
            raise ValueError(
                f"X has {X.shape[1]} features, but model expects {n_features} features. "
                "Provide features or ensure X has the correct number of features."
            )
        
        if labelset is not None:
            if labelset not in self.model_.index.get_level_values("labelset"):
                raise ValueError(f"Labelset '{labelset}' not found in the model.")
            model = self.model_.loc[labelset]
            labelsets = [labelset]
        else:
            model = self.model_
            labelsets = model.index.get_level_values("labelset").unique()
        
        if isinstance(features, pd.DataFrame):
            features = features.index
        elif isinstance(features, pd.Series):
            features = pd.Index(features)

        if features is None:
            logger.debug("No features provided, using full model's features.")
        else:
            if not isinstance(features, pd.Index):
                raise ValueError("features must be a pandas Index or Series.")
            valid_features = features.intersection(self.model_.columns)
            if valid_features.empty:
                raise ValueError("No valid features provided that match the model's features.")
            features_with_prior = valid_features.append(pd.Index([PRIOR]))
            if len(features_with_prior) == self.model_.shape[1]:
                logger.debug("Using full model features including prior.")
            else:
                logger.debug("Using subset of model features including prior.")
                model = model.loc[:, features_with_prior]

        if chunk is None:
            chunks = getattr(X, 'chunks', None)
            if chunks is None:
                chunk = X.shape[0]
            else:
                chunk = chunks[0]
        logger.debug(f"Chunk size for prediction set to {chunk}.")
        
        predictions = pd.DataFrame(index=range(X.shape[0]), columns=labelsets)

        for from_ in range(0, X.shape[0], chunk):
            to_ = min(from_ + chunk, X.shape[0])
            logger.debug(f"Predicting chunk from {from_} to {to_}.")
            X_chunk = X[from_:to_]
            if sp.issparse(X_chunk):
                X_chunk = sp.hstack((X_chunk, np.ones((X_chunk.shape[0], 1))))  # Add prior column
            else:
                X_chunk = np.hstack((X_chunk, np.ones((X_chunk.shape[0], 1))))  # Add prior column
            for labelset in labelsets:
                logger.debug(f"Predicting for labelset: {labelset}.")
                if len(labelsets) > 1:
                    model_subset = model.loc[labelset]
                else:
                    model_subset = model
                if model_subset.empty:
                    continue
                
                log_probs = X_chunk @ model_subset.values.T
                proba = self._normalize_log_probs(log_probs)
                predicted_idx = np.argmax(proba, axis=1)
                predicted_labels = model_subset.index.get_level_values("label").values[predicted_idx]
                conf_score = proba[range(proba.shape[0]), predicted_idx]
                idx = predictions.iloc[from_:to_].index
                predictions.loc[idx, labelset] = predicted_labels.tolist()
                predictions.loc[idx, f"{labelset}_conf"] = conf_score
        logger.debug("Prediction completed.")
        return predictions
    
    @staticmethod
    def _normalize_log_probs(log_probs: np.ndarray) -> np.ndarray:
        """Perform P_i = P_i / sum_i(P_i) but in log space"""
        logger.debug("Start _normalize_log_probs...")
        
        # use log-sum-exp
        k = np.max(log_probs, axis=1).reshape(-1,1)
        exp = np.exp(log_probs - k)
        log_sum_biased = np.log(exp.sum(axis=1).reshape(-1,1))
        log_sum = log_sum_biased + k
        probs = np.exp(log_probs - log_sum)
        logger.debug("Finished _normalize_log_probs!")
        return probs

    def __repr__(self) -> str:
        return repr(self.model_)
    
    def __str__(self) -> str:
        return str(self.model_)
