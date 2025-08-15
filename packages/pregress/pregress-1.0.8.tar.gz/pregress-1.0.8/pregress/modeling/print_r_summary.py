import numpy as np

def print_r_summary(model, summary_df, RSE, r_squared, adj_r_squared, f_statistic, f_p_value):
    """Prints the summary in R style."""
    print("Residuals:")
    print(f"    Min    1Q    Median   3Q    Max ")
    print(f"{min(model.resid): 6.0f} {np.percentile(model.resid, 25): 6.0f} {np.median(model.resid): 6.0f} {np.percentile(model.resid, 75): 6.0f} {max(model.resid): 6.0f}")
    print("")
    print("Coefficients:")
    print(summary_df)
    print("---")
    print("Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1")
    print("")
    print(f"Residual standard error: {RSE:.0f} on {int(model.df_resid)} degrees of freedom")
    print(f"R-squared: {r_squared:.4f}, Adjusted R-squared: {adj_r_squared:.4f}")
    print(f"F-statistic: {f_statistic:.2f} on {int(model.df_model)} and {int(model.df_resid)} DF, p-value: {f_p_value:.6f}")
