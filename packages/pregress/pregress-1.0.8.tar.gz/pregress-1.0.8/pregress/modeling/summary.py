from pregress.modeling.format_summary import format_summary
from pregress.modeling.print_r_summary import print_r_summary
from pregress.modeling.print_anova_table import print_anova_table
from pregress.modeling.print_stata_summary import print_stata_summary
from pregress.modeling.significance_code import significance_code
import numpy as np
import pandas as pd
import statsmodels.api as sm
import warnings
from io import StringIO


def summary(model, out='simple', level=0.95):
    """
    Generates and prints a summary of the regression model fit. The default summary is 'simple',
    but it can also mimic summaries from statsmodels, R, STATA, or show only specific parts like the
    coefficient table or the ANOVA table. The summary is also returned for further use.

    Args:
        model: The regression model object from statsmodels.
        out (str): Type of summary output. Options include 'simple', 'statsmodels', 'R', 'STATA',
                   'coefficients', and 'ANOVA'.
        level (float): Confidence level for the confidence intervals. Option only 
                   applies to the default statsmodels, coefficients, and STATA. 
                   Default is 0.95.

    Returns:
        Various types of summaries depending on the input type, both printed and returned.
    """

    out = out.lower()
    alpha = round(1 - level, 5)  # Ensure alpha is correctly formatted
    
    if out in ['statsmodels', 'stats']:
        print(model.summary(alpha=alpha))
        return
    
    def print_model_type(model):
        if isinstance(model, sm.regression.linear_model.RegressionResultsWrapper):
            if isinstance(model.model, sm.OLS):
                model_type = "ols"
            elif isinstance(model.model, sm.Logit):
                model_type = "logit"
            elif isinstance(model.model, sm.GLM):
                if isinstance(model.model.family, sm.families.Binomial):
                    model_type = "glm"
                else:
                    model_type = "glm_nonlogit"
            else:
                model_type = "Other Regression Model"
        else:
            model_type = "Unsupported model type."

        return model_type

    def summary_ols(model, out='simple', level=0.95):

        alpha = round(1 - level, 5)  # Ensure alpha is correctly formatted

        warnings.filterwarnings("ignore", message="kurtosistest only valid for n>=20")
        warnings.filterwarnings("ignore", category=sm.tools.sm_exceptions.ValueWarning)
        results_summary = model.summary(alpha=alpha)
        results_as_html = results_summary.tables[1].as_html()
        summary_df = pd.read_html(StringIO(results_as_html), header=0, index_col=0)[0]
        summary_df = format_summary(summary_df, alpha)

        p_values = model.pvalues
        conf_intervals = model.conf_int(alpha=alpha)
        r_squared = model.rsquared
        adj_r_squared = model.rsquared_adj
        f_statistic = model.fvalue
        f_p_value = model.f_pvalue
        log_likelihood = model.llf
        aic = model.aic
        bic = model.bic
        RSS = np.sum(model.resid**2)
        df = model.df_resid
        RSE = np.sqrt(RSS / df)
        n_obs = int(model.nobs)
        df_model = model.df_model
        df_resid = model.df_resid
        mse_model = model.mse_model
        mse_resid = model.mse_resid

        if out == 'r':
            print_r_summary(model, summary_df, RSE, r_squared, adj_r_squared, f_statistic, f_p_value)
        elif out == 'simple':
            print("Summary of Regression Analysis:")
            print("======================================================")        
            print("\nCoefficients:")
            print("------------------------------------------------------")
            print(summary_df)
            print("\nModel Statistics:")
            print("------------------------------------------------------")        
            print(f"R-squared: {r_squared:.4f}                AIC: {aic:.4f}")
            print(f"Adj. R-squared: {adj_r_squared:.4f}           BIC: {bic:.4f}")
            print(f"F-statistic: {f_statistic:.2f} on {int(df_model)} and {int(df_resid)} DF, p-value: {f_p_value:.6f}")
            print("======================================================")
        elif out in ['coefficients', 'coef']:
            print(model.summary(alpha=alpha).tables[1])
        elif out == 'anova':
            anova_table = print_anova_table(model)
            print(anova_table)
        elif out == 'stata':
            print_stata_summary(model, summary_df, conf_intervals, level)
        else:
            raise ValueError("Unsupported summary type specified.")

    def summary_logistic(model, out='simple', level=0.95):
        """
        Generates a summary of a logistic regression model using statsmodels.

        Args:
            model: The logistic regression model object from statsmodels.
            out (str): Type of summary output. Options include 'simple', 'statsmodels', 'R', 'STATA',
                      'coefficients', and 'ANOVA' (not typically applicable).
            level (float): Confidence level for the confidence intervals. Default is 0.95.

        Returns:
            Various types of summaries depending on the input type, both printed and returned.
        """

        # Suppress Warnings
        warnings.filterwarnings("ignore", category=FutureWarning, 
                                message="The bic value is computed using the deviance formula.*")
        warnings.filterwarnings("ignore", category=sm.tools.sm_exceptions.ConvergenceWarning)
        
        alpha = round(1 - level, 5)  # Ensure alpha is correctly formatted
        
        results_summary = model.summary(alpha=alpha)
        results_as_html = results_summary.tables[1].as_html()
        summary_df = pd.read_html(StringIO(results_as_html), header=0, index_col=0)[0]
        summary_df = format_summary(summary_df, alpha)

        conf_intervals = model.conf_int(alpha=alpha)
        log_likelihood = model.llf
        aic = model.aic
        bic = model.bic
        pseudo_r_squared = model.pseudo_rsquared(kind='cs')
        n_obs = int(model.nobs)

        if out == 'r':
            print("Not currently available for logistic regression.")
        elif out == 'simple':
            print("Summary of Logistic Regression Analysis:")
            print("======================================================")        
            print("\nCoefficients (Odds Ratios):")
            print("------------------------------------------------------")
            print(summary_df)
            print("\nModel Statistics:")
            print("------------------------------------------------------")        
            print(f"Log-Likelihood: {log_likelihood:.4f}            AIC: {aic:.4f}")
            print(f"Pseudo R-squared: {pseudo_r_squared:.4f}         BIC: {bic:.4f}")
            print("======================================================")
        elif out in ['coefficients', 'coef']:
            print(results_summary.tables[1])
        elif out == 'anova':
            print("ANOVA table not applicable for logistic regression.")
        elif out == 'stata':
            print("Not currently available for logistic regression.")
        else:
            raise ValueError("Unsupported summary type specified.")

        return results_summary

    model_type = print_model_type(model)
    
    if model_type == "ols":
        summary_ols(model, out, level)
    elif model_type == "glm":
        summary_logistic(model, out, level)
    else:
        raise ValueError("Unsupported model type.")
