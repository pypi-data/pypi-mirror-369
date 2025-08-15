import numpy as np

def print_anova_and_summary(model):
    """
    Prints the combined upper left (ANOVA table) and upper right-hand side summary
    of a regression model similar to STATA's output side by side.

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

    # Print the combined summary in the specified format
    print("------------------------------------------------------------------------------")
    print(f"             |      SS       df       MS              Number of obs ={n_obs:>3}")
    print(f"-------------+------------------------------          F({df_model}, {df_resid})      = {f_statistic:.2f}")
    print(f"     Model   | {ssm:10.6f}    {df_model:>2}  {msm:10.6f}           Prob > F      = {f_p_value:.4f}")
    print(f"  Residual   | {ssr:10.6f}    {df_resid:>2}  {msr:10.6f}           R-squared     ={r_squared:>7.4f}")
    print(f"-------------+------------------------------          Adj R-squared = {adj_r_squared:.4f}")
    print(f"     Total   | {sst:10.6f}    {df_total:>2}  {sst/df_total:10.6f}          Root MSE      ={root_mse:>7.4f}")
    print("------------------------------------------------------------------------------")
