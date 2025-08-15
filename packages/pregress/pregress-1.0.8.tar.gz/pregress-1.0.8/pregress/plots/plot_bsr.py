import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def plot_bsr(model, type="predictors", top_n=5, annotate=True, data=None, formula=None, all_features=None):
    """
    Plot results from a best subset regression model.

    Parameters:
    model (statsmodels object): Output of `bsr()` with .bsr_results, .best_by_k, and .bsr_metric.
    type (str): 'line', 'bar', or 'predictors'.
    top_n (int): Number of top models to display (applies to 'bar' and 'predictors').
    annotate (bool): Whether to annotate the best metric value on the plot.
    data (pd.DataFrame): Original data (needed to show all variables in 'predictors' plot).
    formula (str): Original formula (alternative to data for getting all variables).
    all_features (list): Explicit list of all features to show (overrides other methods).
    """
    if not hasattr(model, "bsr_results") or not hasattr(model, "best_by_k") or not hasattr(model, "bsr_metric"):
        raise ValueError("Model must have .bsr_results, .best_by_k, and .bsr_metric attributes.")

    results_df = model.bsr_results.copy()
    feature_col = "Features"
    metric = model.bsr_metric

    metric_column = {
        "adjr2": "Adj. R-squared",
        "aic": "AIC",
        "bic": "BIC",
        "rmse": "RMSE"
    }

    col = metric_column[metric]
    results_df["Num Predictors"] = results_df[feature_col].apply(len)

    # Reconstruct best_df using best_by_k dictionary
    best_rows = []
    for k, feats in model.best_by_k.items():
        match = results_df[results_df[feature_col].apply(lambda f: sorted(f) == sorted(feats))]
        if not match.empty:
            best_rows.append(match.iloc[0])
    best_df = pd.DataFrame(best_rows)
    best_df["Num Predictors"] = best_df[feature_col].apply(len)

    if type == "line":
        plt.figure(figsize=(10, 6))
        plt.plot(best_df["Num Predictors"], best_df[col], marker="o")

        if annotate:
            if metric == "adjr2":
                best_row = best_df.loc[best_df[col].idxmax()]
            else:
                best_row = best_df.loc[best_df[col].idxmin()]
            x = best_row["Num Predictors"]
            y = best_row[col]
            plt.text(x, y, f"{y:.2f}", ha="center", va="bottom", fontweight="bold")

        plt.xlabel("Number of Predictors")
        plt.ylabel(col)
        plt.title(f"{col} by Number of Predictors")
        plt.xticks(np.arange(best_df["Num Predictors"].min(),
                             best_df["Num Predictors"].max() + 1, step=1))
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    elif type == "bar":
        ascending = (metric != "adjr2")
        top = best_df.sort_values(by=col, ascending=ascending).head(top_n)

        plt.figure(figsize=(10, 6))
        bars = plt.bar(top["Num Predictors"], top[col], width=0.6)

        if annotate:
            best_row = top.loc[top[col].idxmax() if metric == "adjr2" else top[col].idxmin()]
            x = best_row["Num Predictors"]
            y = best_row[col]
            plt.text(x, y, f"{y:.2f}", ha='center', va='bottom', fontweight="bold")

        plt.xlabel("Number of Predictors")
        plt.ylabel(col)
        plt.title(f"Top {top_n} Best Models by {col}")

        min_val, max_val = top[col].min(), top[col].max()
        margin = (max_val - min_val) * 0.1 if max_val != min_val else 1
        plt.ylim(min_val - margin, max_val + margin)

        plt.xticks(top["Num Predictors"])
        plt.grid(False)
        plt.tight_layout()
        plt.show()

    elif type == "predictors":
        ascending = (metric != "adjr2")
        top_models = results_df.sort_values(by=col, ascending=ascending).head(top_n)
        
        # Get ALL features with improved logic - preserves xvars order
        all_features_list = _get_all_features_improved(model, data, formula, all_features, results_df, feature_col)

        data_matrix = []
        metric_vals = []

        for _, row in top_models.iterrows():
            feats = row[feature_col]
            metric_val = row[col]
            row_data = [1 if f in feats else 0 for f in all_features_list]
            data_matrix.append(row_data)
            metric_vals.append(f"{metric_val:.3f}")

        heatmap_df = pd.DataFrame(data_matrix, index=metric_vals, columns=all_features_list)
        plt.figure(figsize=(10, len(metric_vals) * 0.5 + 1))
        sns.heatmap(heatmap_df, cmap="Greens", annot=True, fmt="d",
                    linewidths=0.5, linecolor="gray", cbar=False)
        plt.title(f"Top {top_n} Models by {col}")
        plt.xlabel("Predictors")
        plt.ylabel(col)
        plt.tight_layout()
        plt.show()

    else:
        raise ValueError("Invalid type. Choose from: 'line', 'bar', or 'predictors'.")


def _get_all_features_improved(model, data, formula, all_features, results_df, feature_col):
    """
    Get all available features with improved priority order and error handling.
    Preserves order from xvars when available.
    """
    # Priority 1: Check if model has xvars attribute (recommended approach)
    # Preserve the order from xvars - don't sort
    if hasattr(model, 'xvars'):
        return model.xvars
    
    # Priority 2: Explicitly provided all_features
    if all_features is not None:
        return all_features  # Preserve user-provided order
    
    # Priority 3: Check if model has all_features attribute (legacy support)
    if hasattr(model, 'all_features'):
        return model.all_features  # Preserve existing order
    
    # Priority 4: Try to parse formula (with better error handling)
    if data is not None and formula is not None:
        try:
            # Try different import paths for parse_formula
            parse_formula = None
            try:
                from .parse_formula import parse_formula
            except ImportError:
                try:
                    from parse_formula import parse_formula
                except ImportError:
                    # If parse_formula is in the same module or global scope
                    if 'parse_formula' in globals():
                        parse_formula = globals()['parse_formula']
                    else:
                        print("Warning: parse_formula function not found. Using fallback method.")
            
            if parse_formula is not None:
                _, all_vars, _, _ = parse_formula(formula, data)
                # Remove intercept if present and any other non-predictor terms
                # Preserve order from parse_formula
                all_features_list = [var for var in all_vars if var not in ['Intercept', 'intercept']]
                return all_features_list
        
        except Exception as e:
            print(f"Warning: Could not parse formula ({e}). Using fallback method.")
    
    # Priority 5: Try to infer from data columns
    if data is not None:
        # Assume all columns except common response variable names could be features
        # Preserve column order from dataframe
        common_response_names = {'y', 'Y', 'target', 'label', 'outcome', 'response', 'dependent'}
        potential_features = [col for col in data.columns if col.lower() not in common_response_names]
        return potential_features
    
    # Priority 6: Fallback to features found in results (original behavior)
    print("Warning: Using only features found in BSR results. Consider providing 'data', 'formula', or 'all_features' parameter.")
    # Sort only as last resort since we don't have any other ordering information
    return sorted({feat for feats in results_df[feature_col] for feat in feats})
