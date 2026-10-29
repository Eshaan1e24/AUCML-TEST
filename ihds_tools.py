"""Helper classes shared by the notebook and the demo app.

ClipOutliers lives in this file (not inside the notebook) so that the trained models saved with joblib can be loaded
again by the app: pickled objects remember the module in which their class was defined.
"""
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class ClipOutliers(BaseEstimator, TransformerMixin):
    """Cut extreme values of numeric columns so a few typing errors cannot disturb the model.

    During fit() it learns, for every column, the `lower` and `upper` percentile of the TRAINING data.
    During transform() every value below / above those limits is moved to the limit.
    Because the limits are learned on training data only, no information leaks from validation or test data.
    """

    def __init__(self, lower=0.5, upper=99.5):
        # Percentiles used as the lowest and highest allowed value.
        self.lower = lower
        self.upper = upper

    def fit(self, X, y=None):
        """Learn the lower and upper limit of each column from X (training data)."""
        values = np.asarray(X, float)
        self.lower_limits_ = np.nanpercentile(values, self.lower, axis=0)
        self.upper_limits_ = np.nanpercentile(values, self.upper, axis=0)
        return self

    def transform(self, X):
        """Return X with every value moved inside the learned limits."""
        return np.clip(np.asarray(X, float), self.lower_limits_, self.upper_limits_)

    def get_feature_names_out(self, input_features=None):
        """Column names do not change, so return the input names (needed later for SHAP)."""
        return np.asarray(input_features, dtype=object)
