import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

def plot_res(model, res="resid", main="Residual Plot", xlab="Fitted values", ylab="Residuals", subplot=None):
    """
    Plots residuals of a fitted regression model with support for different residual types
    and automatic detection of logistic models.
    
    Args:
        model: A fitted regression model (e.g., statsmodels RegressionResultsWrapper)
        res (str, optional): Type of residuals to plot. Options include:
                           - "resid": Ordinary residuals (default)
                           - "pearson": Pearson residuals
                           - "deviance": Deviance residuals  
                           - "anscombe": Anscombe residuals
                           - "studentized": Studentized residuals
                           - "response": Response residuals
        main (str, optional): Title for the plot. Default: "Residual Plot"
        xlab (str, optional): Label for the x-axis. Default: "Fitted values"
        ylab (str, optional): Label for the y-axis. Default: "Residuals"
        subplot (tuple, optional): A tuple specifying the subplot grid (nrows, ncols, index). 
                                 If None, a new figure is created.
    
    Returns:
        None. Displays a residual plot.
    
    Example:
        >>> import statsmodels.api as sm
        >>> # Linear regression
        >>> model = sm.OLS(y, X).fit()
        >>> plot_res(model, res="pearson")
        >>> 
        >>> # Logistic regression
        >>> logit_model = sm.Logit(y, X).fit()
        >>> plot_res(logit_model, res="deviance")
    """
    try:
        # Detect model type
        model_type = _detect_model_type(model)
        
        # Get residuals based on type
        residuals = _get_residuals(model, res, model_type)
        
        # Get fitted values
        fitted = _get_fitted_values(model, model_type)
        
        # Adjust labels and title based on model type and residual type
        title, x_label, y_label = _adjust_labels(main, xlab, ylab, model_type, res)
        
        # If a subplot is specified, create the subplot; otherwise, create a new figure
        if subplot:
            plt.subplot(*subplot)
        else:
            plt.figure(figsize=(8, 6))
        
        # Create the residual plot
        plt.scatter(fitted, residuals, alpha=0.6, color='blue', edgecolors='black', linewidth=0.5)
        
        # Add reference line (y=0 for most residuals, but different for some types)
        _add_reference_line(model_type, res)
        
        # Add a smooth trend line to help identify patterns
        if len(fitted) > 10:  # Only add trend line if we have enough points
            try:
                z = np.polyfit(fitted, residuals, 1)
                trend_line = np.poly1d(z)
                sorted_fitted = np.sort(fitted)
                plt.plot(sorted_fitted, trend_line(sorted_fitted), 'orange', linestyle='-', alpha=0.8, linewidth=1)
            except:
                pass  # Skip trend line if fitting fails
        
        # Setting the title and labels
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)
        plt.grid(True, alpha=0.3)
        
        # Show the plot only if no subplot is provided
        if subplot is None:
            plt.tight_layout()
            plt.show()
        
    except Exception as e:
        raise RuntimeError(f"Error creating residual plot: {e}")


def _detect_model_type(model):
    """
    Automatically detect the type of statsmodels regression model.
    
    Returns:
        str: 'logistic', 'linear', or 'other'
    """
    model_class = model.__class__.__name__
    model_module = model.__class__.__module__
    
    # Check for logistic regression models
    if ('Logit' in model_class or 
        'logit' in model_class.lower() or
        'BinaryResults' in model_class or
        'LogitResults' in model_class):
        return 'logistic'
    
    # Check for Poisson, Negative Binomial, etc.
    elif any(name in model_class for name in ['Poisson', 'NegativeBinomial', 'Gamma']):
        return 'glm'
    
    # Check for linear regression models
    elif ('OLS' in model_class or 
          'WLS' in model_class or 
          'GLS' in model_class or
          'RegressionResults' in model_class):
        return 'linear'
    
    # Try to infer from model attributes
    elif hasattr(model, 'family'):
        family_name = str(model.family).lower()
        if 'binomial' in family_name:
            return 'logistic'
        elif any(name in family_name for name in ['poisson', 'gamma', 'negativebinomial']):
            return 'glm'
        else:
            return 'linear'
    
    return 'other'


def _get_residuals(model, res_type, model_type):
    """
    Extract the specified type of residuals from the model.
    """
    # Map common residual names to their actual attribute names
    residual_mapping = {
        'resid': 'resid',
        'pearson': 'resid_pearson',
        'deviance': 'resid_deviance',
        'anscombe': 'resid_anscombe',
        'studentized': 'resid_studentized',
        'response': 'resid_response'
    }
    
    if res_type not in residual_mapping:
        available_types = list(residual_mapping.keys())
        raise ValueError(f"Invalid residual type '{res_type}'. Available types: {available_types}")
    
    attr_name = residual_mapping[res_type]
    
    if hasattr(model, attr_name):
        return getattr(model, attr_name)
    else:
        # Fallback options
        if res_type == 'resid' and hasattr(model, 'resid'):
            return model.resid
        elif hasattr(model, 'resid'):
            print(f"Warning: {res_type} not available for this model type. Using ordinary residuals.")
            return model.resid
        else:
            raise AttributeError(f"Model does not have residuals of type '{res_type}' or basic 'resid' attribute")


def _get_fitted_values(model, model_type):
    """
    Get fitted values appropriate for the model type.
    """
    if hasattr(model, 'fittedvalues'):
        fitted = model.fittedvalues
    elif hasattr(model, 'predict'):
        fitted = model.predict()
    else:
        raise AttributeError("Model must have either 'fittedvalues' attribute or 'predict()' method")
    
    # For logistic regression, we might want to use linear predictor instead of probabilities
    if model_type == 'logistic':
        # Try to get linear predictor (log-odds) if available
        if hasattr(model, 'linear_pred'):
            return model.linear_pred
        elif hasattr(model, 'predict') and hasattr(model, 'params'):
            # Calculate linear predictor manually
            try:
                if hasattr(model.model, 'exog'):
                    return np.dot(model.model.exog, model.params)
            except:
                pass
    
    return fitted


def _adjust_labels(main, xlab, ylab, model_type, res_type):
    """
    Adjust plot labels based on model type and residual type.
    """
    # Adjust main title if it's the default
    if main == "Residual Plot":
        if model_type == 'logistic':
            if res_type == 'resid':
                title = "Logistic Regression Residual Plot"
            else:
                title = f"Logistic Regression {res_type.title()} Residual Plot"
        elif model_type == 'glm':
            if res_type == 'resid':
                title = "GLM Residual Plot"
            else:
                title = f"GLM {res_type.title()} Residual Plot"
        else:
            if res_type == 'resid':
                title = "Residual Plot"
            else:
                title = f"{res_type.title()} Residual Plot"
    else:
        title = main
    
    # Adjust x-axis label if it's the default
    if xlab == "Fitted values":
        if model_type == 'logistic':
            x_label = "Linear Predictor (Log-odds)"
        else:
            x_label = "Fitted values"
    else:
        x_label = xlab
    
    # Adjust y-axis label if it's the default
    if ylab == "Residuals":
        if res_type == 'resid':
            y_label = "Residuals"
        else:
            y_label = res_type.title() + " Residuals"
    else:
        y_label = ylab
    
    return title, x_label, y_label


def _add_reference_line(model_type, res_type):
    """
    Add appropriate reference line based on model and residual type.
    """
    # Most residuals should center around 0
    plt.axhline(0, color='red', linestyle='--', linewidth=1, alpha=0.8)
    
    # For some specific cases, you might want additional reference lines
    if model_type == 'logistic' and res_type in ['pearson', 'deviance']:
        # Could add ±2 lines for rough 95% bounds
        plt.axhline(2, color='red', linestyle=':', linewidth=0.5, alpha=0.5)
        plt.axhline(-2, color='red', linestyle=':', linewidth=0.5, alpha=0.5)
