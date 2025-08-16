import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score


def get_metrics(true, pred):
    """Get metrics for a regression problem.

    Args:
        true (np.ndarray): true values
        pred (np.ndarray): predicted values

    Returns:
        dict: dictionary of metrics
    """

    metrics = {}
    metrics["mae"] = mean_absolute_error(true, pred)
    metrics["rmse"] = np.sqrt(mean_squared_error(true, pred))
    metrics["r2"] = r2_score(true, pred)
    metrics["mdae"] = median_absolute_error(true, pred)
    return metrics
