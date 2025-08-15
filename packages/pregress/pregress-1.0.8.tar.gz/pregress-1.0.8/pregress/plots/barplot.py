from pregress.modeling.parse_formula import parse_formula
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def barplot(formula=None, data=None, xcolor="blue", ycolor="red", title="Barplots of Variables", xlab="Variable", ylab="Value", subplot=None):
    """
    Generates and prints bar plots for all numeric variables specified in the formula or all numeric variables in the data if no formula is provided.

    Args:
        formula (str, optional): Formula to define the model (dependent ~ independent).
        data (DataFrame, optional): Data frame containing the data.
        xcolor (str, optional): Color of the bars for the independent variables.
        ycolor (str, optional): Color of the bars for the dependent variable.
        title (str, optional): Title of the plot.
        xlab (str, optional): Label for the x-axis.
        ylab (str, optional): Label for the y-axis.
        subplot (tuple, optional): A tuple specifying the subplot grid (nrows, ncols, index).
                                   If None, a new figure is created.

    Returns:
        None. The function creates and shows bar plots.
    """
    if isinstance(formula, pd.DataFrame):
        data = formula
        formula = None
    if formula is not None:
        formula = formula + "+0"
        Y_name, X_names, Y_out, X_out = parse_formula(formula, data)

        # Combine Y and X data for bar plots
        plot_data = pd.concat([pd.Series(Y_out, name=Y_name), X_out], axis=1)

        # Melt the DataFrame for easier plotting with seaborn
        plot_data_melted = plot_data.melt(var_name='Variable', value_name='Value')

        # Create a color mapping for columns
        palette = {Y_name: ycolor}
        palette.update({x: xcolor for x in X_names})

    else:
        # If no formula is provided, use all numeric variables in the data
        plot_data = data.select_dtypes(include=[np.number])

        # Melt the DataFrame for easier plotting with seaborn
        plot_data_melted = plot_data.melt(var_name='Variable', value_name='Value')

        # Create a single color mapping for all variables
        palette = {var: xcolor for var in plot_data_melted['Variable'].unique()}

    # If a subplot is specified, create a subplot within the given grid; otherwise, use a new figure
    if subplot:
        plt.subplot(*subplot)
    else:
        plt.figure(figsize=(10, 6))

    # Create the bar plot
    sns.barplot(x='Variable', y='Value', data=plot_data_melted, hue='Variable', dodge=False, palette=palette, errorbar=None, legend=False)

    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel(ylab)

    # Show the plot only if no subplot is provided
    if subplot is None:
        plt.show()
        plt.clf()
        plt.close()
