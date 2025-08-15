from scipy.stats import shapiro
import statsmodels.api as sm
import numpy as np

def shapiro_test(input_data, out=True):
    """
    Perform the Shapiro-Wilk test for normality on a given vector or statsmodels regression results object.

    Args:
        input_data (array-like or statsmodels.regression.linear_model.RegressionResultsWrapper): Input data or a fitted statsmodels regression model.
        out (bool): If True, prints the test details.

    Returns:
        tuple: The test statistic and the p-value of the Shapiro-Wilk test.
    """
    # Check if input_data is a statsmodels object
    if isinstance(input_data, sm.regression.linear_model.RegressionResultsWrapper):
        # Use the residuals from the model
        data = input_data.resid
    else:
        # Assume input_data is a vector
        data = np.asarray(input_data)

    # Perform the Shapiro-Wilk test
    stat, p_value = shapiro(data)

    # Determine the result
    alpha = 0.05
    if p_value > alpha:
        result = 'Normal'
    else:
        result = 'Non-normal'

    # Optionally print the details
    if out:
        print("Shapiro-Wilk Test for Normality")
        print("================================")
        print(f"Test Statistic : {stat:.4f}")
        print(f"P-value        : {p_value:.4g}")
        print(f"Result         : {result}")
        print("================================")

    # Return the test statistic and p-value
    return
