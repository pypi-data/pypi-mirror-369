from pregress.modeling.parse_formula import parse_formula
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def boxplot(formula=None, data=None, xcolor="blue", ycolor="red", title="Boxplots of Variables", xlab="Variable", ylab="Value", subplot=None, **kwargs):
    """
    Generates and prints boxplots for:
    - All numeric variables in the data if no formula is provided.
    - Variables specified in the formula.
    - A grouped boxplot when Y is numeric and X is categorical.
    Args:
        formula (str, optional): Formula to define the model (e.g., Y ~ X).
        data (DataFrame, optional): Data frame containing the data.
        xcolor (str, optional): Color of the boxplots for the predictor variables.
        ycolor (str, optional): Color of the boxplots for the response variable.
        title (str, optional): Title of the plot.
        xlab (str, optional): Label for the x-axis.
        ylab (str, optional): Label for the y-axis.
        subplot (tuple, optional): A tuple specifying the subplot grid (nrows, ncols, index).
                                   If None, a new figure is created.
        **kwargs: Additional keyword arguments passed to seaborn.boxplot().
    Returns:
        None. The function creates and shows boxplots.
    """
    if isinstance(formula, pd.DataFrame):
        data = formula
        formula = None
    
    if formula is not None:
        # Parse the original formula to get variable names before transformation
        original_formula = formula
        formula = formula + "+0"
        Y_name, X_names, Y_out, X_out = parse_formula(formula, data)
        
        # Extract the original predictor variable name from the formula
        # This handles the case where parse_formula transforms categorical variables
        original_x_var = original_formula.split('~')[1].strip().split('+')[0].strip()
        
        # Check if we have a single categorical predictor (special case)
        if (len(X_names) >= 1 and original_x_var in data.columns and 
            (pd.api.types.is_categorical_dtype(data[original_x_var]) or 
             data[original_x_var].dtype == object)):
            
            # Special case: Y is numeric, X is categorical
            plot_data = pd.DataFrame({
                Y_name: Y_out,
                original_x_var: data[original_x_var]
            })
            if subplot:
                plt.subplot(*subplot)
            else:
                plt.figure(figsize=(10, 6))
            sns.boxplot(x=original_x_var, y=Y_name, data=plot_data, color=ycolor, **kwargs)
            plt.title(title)
            plt.xlabel(xlab if xlab != "Variable" else original_x_var)
            plt.ylabel(ylab if ylab != "Value" else Y_name)
            plt.tight_layout()
            if subplot is None:
                plt.show()
                plt.clf()
                plt.close()
            return
        
        # Otherwise, proceed with normal case: multiple numeric predictors
        # Filter out intercept and non-numeric columns from X_out
        if hasattr(X_out, 'columns'):
            numeric_predictors = X_out.select_dtypes(include=[np.number])
            # Remove intercept columns
            numeric_predictors = numeric_predictors.drop(['Intercept', 'const'], axis=1, errors='ignore')
        else:
            numeric_predictors = X_out
        
        # Combine Y and numeric predictors
        if isinstance(Y_out, pd.Series):
            plot_data = pd.concat([Y_out, numeric_predictors], axis=1)
        else:
            plot_data = pd.concat([pd.Series(Y_out, name=Y_name), numeric_predictors], axis=1)
        
        plot_data_melted = plot_data.melt(var_name='Variable', value_name='Value')
        palette = {Y_name: ycolor}
        # Add colors for the actual predictor columns
        palette.update({col: xcolor for col in numeric_predictors.columns})
    else:
        # No formula provided, use all numeric columns
        plot_data = data.select_dtypes(include=[np.number])
        plot_data_melted = plot_data.melt(var_name='Variable', value_name='Value')
        palette = {var: xcolor for var in plot_data_melted['Variable'].unique()}
    
    if subplot:
        plt.subplot(*subplot)
    else:
        plt.figure(figsize=(10, 6))
    
    sns.boxplot(x='Variable', y='Value', data=plot_data_melted, palette=palette, dodge=False, **kwargs)
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.tight_layout()
    if subplot is None:
        plt.show()
        plt.clf()
        plt.close()
