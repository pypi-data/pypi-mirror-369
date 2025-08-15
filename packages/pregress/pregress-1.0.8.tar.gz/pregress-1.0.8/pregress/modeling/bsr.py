import numpy as np
import pandas as pd
from itertools import combinations
from .fit import fit
from .parse_formula import parse_formula

def bsr(formula, data, max_var=8, metric="aic", method="ols"):
    """
    Perform Best Subset Regression using either OLS or Logistic regression.
    
    Parameters:
        formula (str): A regression formula (e.g., 'Y ~ X1 + X2').
        data (pd.DataFrame): Dataset containing the variables.
        max_var (int): Max number of predictors to consider.
        metric (str): One of 'adjr2', 'aic', 'bic', or 'rmse'.
        method (str): 'ols' for linear regression or 'logistic' for binary logistic regression.
    Returns:
        Fitted statsmodels model with attributes:
            - best_features
            - best_by_k
            - bsr_results
            - bsr_metric
    """
    # Parse the formula
    y_var, x_vars, Y, X = parse_formula(formula, data)
    
    # CRITICAL FIX: Use actual column names from X DataFrame instead of x_vars
    # This handles cases where parse_formula creates dummy variables with different names
    if hasattr(X, 'columns'):
        actual_predictors = [col for col in X.columns if col not in ['Intercept', 'const']]
    else:
        # Fallback to original logic if X is not a DataFrame
        actual_predictors = [var for var in x_vars if var not in ['Intercept', 'const']]
    
    def get_subsets(variables, max_size):
        return [subset for k in range(1, max_size + 1) for subset in combinations(variables, k)]
    
    def get_metrics(model):
        n = model.nobs
        p = model.df_model + 1
        if method == "ols":
            mse = np.sum(model.resid ** 2) / (n - p)
            rmse = np.sqrt(mse)
        else:
            rmse = np.nan  # not defined for logistic
        return model.rsquared_adj if hasattr(model, "rsquared_adj") else np.nan, model.aic, model.bic, rmse
    
    # Validate inputs early
    metric_column = {"adjr2": "Adj. R-squared", "aic": "AIC", "bic": "BIC", "rmse": "RMSE"}
    if metric not in metric_column:
        raise ValueError("Invalid metric. Choose from: 'adjr2', 'aic', 'bic', 'rmse'.")
    
    if method == "logistic" and metric == "rmse":
        raise ValueError("RMSE is not valid for logistic regression.")
    
    if len(actual_predictors) == 0:
        raise ValueError("No predictor variables found after parsing formula.")
    
    # Ensure max_var is reasonable
    max_var = min(max_var, len(actual_predictors))
    if max_var <= 0:
        raise ValueError("max_var must be positive and there must be predictor variables.")
    
    subsets = get_subsets(actual_predictors, max_var)
    results = []
    failed_subsets = []
    
    for subset in subsets:
        try:
            # CRITICAL FIX: Build formula using actual column names
            # Create a subset of X with only the selected columns
            X_subset = X[list(subset)]
            
            # Add intercept if it was in the original X
            if 'Intercept' in X.columns:
                X_subset = pd.concat([X[['Intercept']], X_subset], axis=1)
            elif 'const' in X.columns:
                X_subset = pd.concat([X[['const']], X_subset], axis=1)
            
            # Fit model directly with X_subset and Y instead of using formula
            if method.lower() == "ols":
                import statsmodels.api as sm
                model = sm.OLS(Y, X_subset).fit()
            elif method.lower() == "logistic":
                import statsmodels.api as sm
                # Check and convert Y if necessary for logistic regression
                Y_logistic = Y
                if not pd.api.types.is_numeric_dtype(Y_logistic):
                    Y_logistic = pd.get_dummies(Y_logistic, drop_first=True)
                    if Y_logistic.shape[1] > 1:
                        failed_subsets.append((subset, "Multi-class response not supported"))
                        continue
                model = sm.GLM(Y_logistic, X_subset, family=sm.families.Binomial()).fit()
            else:
                raise NotImplementedError(f"Method '{method}' is not implemented.")
            
            adjr2, aic, bic, rmse = get_metrics(model)
            results.append((subset, adjr2, aic, bic, rmse))
            
        except Exception as e:
            failed_subsets.append((subset, str(e)))
            continue
    
    if not results:
        raise RuntimeError(f"No models could be fitted successfully. Failed subsets: {failed_subsets}")
    
    results_df = pd.DataFrame(results, columns=["Features", "Adj. R-squared", "AIC", "BIC", "RMSE"])
    
    # Handle NaN values in the metric column before sorting
    metric_col = metric_column[metric]
    if results_df[metric_col].isna().all():
        raise ValueError(f"All models have NaN values for metric '{metric}'. Check your data and model specification.")
    
    # Remove rows with NaN in the metric column before sorting
    results_df_clean = results_df.dropna(subset=[metric_col])
    if results_df_clean.empty:
        raise ValueError(f"No valid models found for metric '{metric}' after removing NaN values.")
    
    ascending = metric != "adjr2"
    results_df_clean = results_df_clean.sort_values(by=metric_col, ascending=ascending)
    
    best_features = list(results_df_clean.iloc[0]['Features'])
    
    # Fit the final best model using the same direct approach
    X_best = X[best_features]
    if 'Intercept' in X.columns:
        X_best = pd.concat([X[['Intercept']], X_best], axis=1)
    elif 'const' in X.columns:
        X_best = pd.concat([X[['const']], X_best], axis=1)
    
    if method.lower() == "ols":
        best_model = sm.OLS(Y, X_best).fit()
    elif method.lower() == "logistic":
        Y_logistic = Y
        if not pd.api.types.is_numeric_dtype(Y_logistic):
            Y_logistic = pd.get_dummies(Y_logistic, drop_first=True)
        best_model = sm.GLM(Y_logistic, X_best, family=sm.families.Binomial()).fit()
    
    # Calculate best_by_k
    best_by_k = {}
    k_groups = results_df_clean.groupby(results_df_clean["Features"].apply(len))
    
    for k, group in k_groups:
        if ascending:
            best_row = group.loc[group[metric_col].idxmin()]
        else:
            best_row = group.loc[group[metric_col].idxmax()]
        best_by_k[k] = list(best_row['Features'])
    
    # Attach results to the best model
    best_model.best_features = best_features
    best_model.best_by_k = best_by_k
    best_model.bsr_results = results_df  # Keep original results (including NaN)
    best_model.bsr_results_clean = results_df_clean  # Add cleaned results
    best_model.bsr_metric = metric
    best_model.xvars = actual_predictors  # Use actual predictors
    best_model.failed_subsets = failed_subsets  # Add info about failed fits
    
    return best_model
