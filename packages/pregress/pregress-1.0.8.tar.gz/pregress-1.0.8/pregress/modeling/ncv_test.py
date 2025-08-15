
import numpy as np
import statsmodels.api as sm
from scipy.stats import chi2

def ncv_test(model, out=True):
    """
    Replicates R's car::ncvTest using a score test formulation,
    assuming intercept is already included and labeled "Intercept".

    Args:
        model: A fitted statsmodels OLS regression model.
        out (bool): If True, prints results.

    Returns:
        float: The p-value of the test.
    """
    resid_sq = model.resid ** 2
    n = len(resid_sq)
    sigma2 = np.mean(resid_sq)
    fitted = model.fittedvalues

    # Use intercept already in model: construct aux_X accordingly
    aux_X = np.column_stack((np.ones_like(fitted), fitted))  # manually add intercept

    # Auxiliary response for score test
    f = resid_sq / sigma2 - 1

    # Fit auxiliary model
    aux_model = sm.OLS(f, aux_X).fit()
    test_stat = 0.5 * np.sum(aux_model.fittedvalues ** 2)
    df = aux_model.df_model
    p_value = 1 - chi2.cdf(test_stat, df=df)

    if out:
        print("Nonconstant Variance Test")
        print("========================================")
        print(f"Test Statistic      : {test_stat:.4f}")
        print(f"P-value             : {p_value:.4g}")
        print(f"Result              : {'Heteroscedastic (p < 0.05)' if p_value < 0.05 else 'Homoscedastic (p ≥ 0.05)'}")
        print("========================================")

    return

