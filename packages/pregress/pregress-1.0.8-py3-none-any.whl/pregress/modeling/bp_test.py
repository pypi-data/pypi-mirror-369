import numpy as np
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan

def bp_test(model, use_fitted=False, out=True):
    """
    Perform the Breusch-Pagan test for heteroscedasticity.

    Args:
        model: A fitted statsmodels regression model.
        use_fitted (bool): If True, test against fitted values (R's ncvTest equivalent).
        out (bool): If True, print test details.

    Returns:
        float: p-value of the test.
    """
    if use_fitted:
        fitted = model.fittedvalues
        # Add constant only if not already present
        has_const = 'Intercept' in model.model.exog_names or 'const' in model.model.exog_names
        if has_const:
            x = np.column_stack((np.ones_like(fitted), fitted))
        else:
            x = sm.add_constant(fitted)
    else:
        x = model.model.exog

    bp_stat, p_value, _, _ = het_breuschpagan(model.resid, x)

    if out:
        print("Breusch-Pagan Test for Heteroscedasticity")
        print("========================================")
        print(f"Test Statistic : {bp_stat:.4f}")
        print(f"P-value        : {p_value:.4g}")
        print(f"Result         : {'Heteroscedastic (p < 0.05)' if p_value < 0.05 else 'Homoscedastic (p ≥ 0.05)'}")
        print("========================================")

    return
