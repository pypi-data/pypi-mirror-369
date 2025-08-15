import statsmodels.api as sm
from .parse_formula import parse_formula
from .fit import fit

def step(formula, data, direction='backward', metric='aic', threshold_in=0.05, threshold_out=0.10, max_steps=100, verbose=False):
    """
    Perform stepwise model selection based on a specified metric.

    Parameters:
    ----------
    formula : str
        A regression formula of the form 'Y ~ X1 + X2 + ...'.
    data : pandas.DataFrame
        The dataset containing the variables in the formula.
    direction : {'forward', 'backward', 'both'}, default='backward'
        Direction of selection:
        - 'forward': starts with the intercept only and adds variables.
        - 'backward': starts with all variables and removes variables.
        - 'both': combination of forward and backward steps.
    metric : {'aic', 'bic', 'adjr2', 'pvalue'}, default='aic'
        The metric used to evaluate model performance at each step.
        - 'aic': Akaike Information Criterion.
        - 'bic': Bayesian Information Criterion.
        - 'adjr2': Adjusted R-squared.
        - 'pvalue': Highest p-value among predictors (excluding intercept).
    threshold_in : float, default=0.05
        (Currently unused) Intended threshold for including a variable based on p-value.
    threshold_out : float, default=0.10
        (Currently unused) Intended threshold for removing a variable based on p-value.
    max_steps : int, default=100
        Maximum number of steps to take before stopping.
    verbose : bool, default=False
        If True, prints progress messages showing each step taken.

    Returns:
    -------
    model : statsmodels object
        The final selected model, with additional attributes accessible through standard statsmodels API.
    """

    def get_score(model):
        if metric == 'aic':
            return model.aic
        elif metric == 'bic':
            return model.bic
        elif metric == 'adjr2':
            return 1 - (1 - model.rsquared) * (model.nobs - 1) / (model.nobs - model.df_model - 1)
        elif metric == 'pvalue':
            # Handle intercept names more robustly
            intercept_names = ['Intercept', 'const', 'Const']
            pvals_no_intercept = model.pvalues.copy()
            for intercept_name in intercept_names:
                pvals_no_intercept = pvals_no_intercept.drop(intercept_name, errors="ignore")
            return pvals_no_intercept.max() if len(pvals_no_intercept) > 0 else 0
        else:
            raise ValueError("Invalid metric")

    # Parse to get variable names and transformed data
    Y_name, X_names, Y_out, X_out = parse_formula(formula, data)

    # CRITICAL FIX: Use actual column names from X_out instead of X_names
    # This handles cases where parse_formula creates dummy variables with different names
    if hasattr(X_out, 'columns'):
        actual_predictors = [col for col in X_out.columns if col not in ['Intercept', 'const']]
        has_intercept = any(col in X_out.columns for col in ['Intercept', 'const'])
        intercept_col = 'Intercept' if 'Intercept' in X_out.columns else ('const' if 'const' in X_out.columns else None)
    else:
        # Fallback to original logic if X_out is not a DataFrame
        actual_predictors = [var for var in X_names if var not in ['Intercept', 'const']]
        has_intercept = 'Intercept' in X_names
        intercept_col = 'Intercept'

    label = metric.upper()

    # Correct initialization of selected and remaining variables
    if direction in ['forward', 'both']:
        selected = [intercept_col] if has_intercept and intercept_col else []
        remaining = actual_predictors.copy()
    else:  # backward only
        selected = ([intercept_col] if has_intercept and intercept_col else []) + actual_predictors.copy()
        remaining = []

    # Builds model from selected variables using direct fitting approach
    def model_from_vars(vars):
        if not vars or (len(vars) == 1 and vars[0] in ['Intercept', 'const']):
            # Intercept-only model
            if has_intercept and intercept_col:
                X_subset = X_out[[intercept_col]]
            else:
                # Create intercept if needed
                import pandas as pd
                X_subset = pd.DataFrame({'Intercept': [1] * len(Y_out)}, index=Y_out.index)
        else:
            # Model with predictors
            predictor_vars = [v for v in vars if v not in ['Intercept', 'const']]
            if predictor_vars:
                X_subset = X_out[predictor_vars]
                # Add intercept if it should be included
                if has_intercept and intercept_col and intercept_col in vars:
                    import pandas as pd
                    X_subset = pd.concat([X_out[[intercept_col]], X_subset], axis=1)
                elif not has_intercept or intercept_col not in vars:
                    # No intercept case - this is handled by statsmodels
                    pass
            else:
                # Only intercept
                if has_intercept and intercept_col:
                    X_subset = X_out[[intercept_col]]
                else:
                    import pandas as pd
                    X_subset = pd.DataFrame({'Intercept': [1] * len(Y_out)}, index=Y_out.index)
        
        # Fit model directly
        model = sm.OLS(Y_out, X_subset).fit()
        return model

    best_model = model_from_vars(selected)
    current_score = get_score(best_model)

    if verbose:
        print(f"Initial {label} = {current_score:.4f}")
        print(f"Initial variables: {[v for v in selected if v not in ['Intercept', 'const']]}")

    step_count = 0
    while step_count < max_steps:
        step_count += 1
        changed = False

        # Forward step
        if direction in ['forward', 'both']:
            scores = []
            for var in remaining:
                trial_vars = selected + [var]
                try:
                    model = model_from_vars(trial_vars)
                    score = get_score(model)
                    scores.append((score, var, model))
                except Exception as e:
                    if verbose:
                        print(f"Failed to fit model with {var}: {e}")
                    continue
            
            if scores:
                best = min(scores, key=lambda x: x[0]) if metric in ['aic', 'bic', 'pvalue'] else max(scores, key=lambda x: x[0])
                if (metric in ['aic', 'bic', 'pvalue'] and best[0] < current_score) or \
                   (metric == 'adjr2' and best[0] > current_score):
                    selected.append(best[1])
                    remaining.remove(best[1])
                    best_model = best[2]
                    current_score = best[0]
                    changed = True
                    if verbose:
                        print(f"Step {step_count}: add {best[1]} ({label}={current_score:.4f})")

        # Backward step
        if direction in ['backward', 'both']:
            # Only consider removing non-intercept variables
            removable_vars = [v for v in selected if v not in ['Intercept', 'const']]
            if removable_vars:
                scores = []
                for var in removable_vars:
                    trial_vars = [v for v in selected if v != var]
                    try:
                        model = model_from_vars(trial_vars)
                        score = get_score(model)
                        scores.append((score, var, model))
                    except Exception as e:
                        if verbose:
                            print(f"Failed to fit model without {var}: {e}")
                        continue
                
                if scores:
                    best = min(scores, key=lambda x: x[0]) if metric in ['aic', 'bic', 'pvalue'] else max(scores, key=lambda x: x[0])
                    if (metric in ['aic', 'bic', 'pvalue'] and best[0] < current_score) or \
                       (metric == 'adjr2' and best[0] > current_score):
                        selected.remove(best[1])
                        remaining.append(best[1])
                        best_model = best[2]
                        current_score = best[0]
                        changed = True
                        if verbose:
                            print(f"Step {step_count}: remove {best[1]} ({label}={current_score:.4f})")

        if not changed:
            if verbose:
                print(f"No improvement found. Stopping at step {step_count}.")
            break

    if verbose:
        final_vars = [v for v in selected if v not in ['Intercept', 'const']]
        print(f"Final model variables: {final_vars}")
        print(f"Final {label} = {current_score:.4f}")

    return best_model
