import numpy as np
import pandas as pd

def print_anova_table(model):
    """
    Prints the ANOVA table for a given model.

    Args:
        model: A fitted statsmodels regression model.
    """
    # Number of observations
    n_obs = int(model.nobs)

    # F-statistic and its p-value
    f_statistic = model.fvalue
    f_p_value = model.f_pvalue

    # Degrees of freedom for the model and residuals
    df_model = int(model.df_model)
    df_resid = int(model.df_resid)
    df_total = df_model + df_resid

    # R-squared and Adjusted R-squared
    r_squared = model.rsquared
    adj_r_squared = model.rsquared_adj

    # Root Mean Squared Error (Root MSE)
    root_mse = np.sqrt(model.mse_resid)

    # Sum of Squares
    ssr = np.sum(model.resid ** 2)  # Residual Sum of Squares
    ssm = np.sum((model.fittedvalues - np.mean(model.model.endog)) ** 2)  # Model Sum of Squares
    sst = ssr + ssm  # Total Sum of Squares

    # Mean Squares
    msr = ssr / df_resid  # Residual Mean Square
    msm = ssm / df_model  # Model Mean Square

    # Create ANOVA table
    anova_table = pd.DataFrame({
        'df': [df_model, df_resid, df_total],
        'sum_sq': [ssm, ssr, sst],
        'mean_sq': [msm, msr, ""],
        'F': [f_statistic, "", ""],
        'Pr(>F)': [f'{f_p_value:.4f}', "", ""]
    }, index=['Regression', 'Residual', 'Total'])

    return anova_table
