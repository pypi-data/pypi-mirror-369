import numpy as np
import pandas as pd
import statsmodels.api as sm

def abline(intercept, slope, num_points=100):
    """
    Creates a statsmodels OLS object with a manually specified slope and intercept.

    Args:
        intercept (float): The intercept of the line.
        slope (float): The slope of the line.
        num_points (int, optional): The number of points to generate. Default is 100.

    Returns:
        model (statsmodels.regression.linear_model.RegressionResultsWrapper): The fitted OLS model.
    """
    # Create predictor variable
    X = np.linspace(0, 10, num_points)
    
    # Compute response variable using the specified slope and intercept
    Y = intercept + slope * X
    
    # Create a DataFrame for the predictor
    data = pd.DataFrame({'X': X})
    
    # Add a constant term for the intercept
    data['Intercept'] = 1
    
    # Reorder columns to ensure 'Intercept' comes first
    data = data[['Intercept', 'X']]
    
    # Fit the OLS model
    model = sm.OLS(Y, data).fit()
    
    return model
