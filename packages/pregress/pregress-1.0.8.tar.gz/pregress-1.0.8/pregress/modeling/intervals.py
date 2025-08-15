import numpy as np
import pandas as pd

def intervals(model, newX, interval='confidence', level=0.95):
    """
    Calculate confidence or prediction intervals for a statsmodels object.

    Parameters:
    model : statsmodels object
        The fitted statsmodels model.
    newX : DataFrame
        DataFrame of predictor variables.
    interval : str
        Type of interval to calculate, either 'confidence' or 'prediction'.
    level : float
        The confidence level for the intervals. Default is 0.95.

    Returns:
    intervals : DataFrame
        DataFrame with lower bound, prediction, and upper bound.
    """
    if not isinstance(newX, pd.DataFrame):
        newX = pd.DataFrame(newX)

    model_columns = model.model.exog_names

    # Check if newX already has a column named 'intercept' or 'const' (case-insensitive)
    has_intercept = any(col.lower() == 'intercept' or col.lower() == 'const' for col in newX.columns)

    # Insert the intercept column if it's required by the model and not present in newX
    if not has_intercept:
        if 'Intercept' in model_columns:
            newX.insert(0, 'Intercept', 1)
        elif 'const' in model_columns:
            newX.insert(0, 'const', 1)
        elif 'intercept' in model_columns:
            newX.insert(0, 'intercept', 1)

    preds = model.get_prediction(newX)
    alpha = 1 - level
    summary_frame = preds.summary_frame(alpha=alpha)

    if interval == 'confidence':
        lower_bound = summary_frame['mean_ci_lower']
        upper_bound = summary_frame['mean_ci_upper']
    elif interval == 'prediction':
        lower_bound = summary_frame['obs_ci_lower']
        upper_bound = summary_frame['obs_ci_upper']
    else:
        raise ValueError("Interval must be 'confidence' or 'prediction'")

    prediction = summary_frame['mean']

    intervals = pd.DataFrame({
        'Lower Bound': lower_bound,
        'Prediction': prediction,
        'Upper Bound': upper_bound
    })

    return intervals
