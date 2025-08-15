import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pregress.modeling.parse_formula import parse_formula


def plot_cor(formula, data=None, main='Correlation Matrix', xlab='Variables', ylab='Variables', subplot=None, **kwargs):
    """
    Generates a heatmap for the correlation matrix of a dataframe.

    Args:
        formula (str or pandas.DataFrame): The formula or dataframe for which to compute the correlation matrix.
        data (pandas.DataFrame, optional): The dataframe for formula evaluation if a formula is provided.
        main (str, optional): Main title of the plot.
        xlab (str, optional): Label for the x-axis.
        ylab (str, optional): Label for the y-axis.
        subplot (tuple, optional): Subplot for embedding the heatmap (nrows, ncols, index).
        kwargs: Additional keyword arguments for sns.heatmap() (e.g., annot, cmap, square, vmax, vmin, linewidths, etc.)

    Returns:
        None. Displays the heatmap.
    """

    if isinstance(formula, pd.DataFrame):
        data = formula
        formula = None

    if formula is not None:
        formula = formula + "+0"
        Y_name, X_names, Y_out, X_out = parse_formula(formula, data)
        # Combine Y and X data for the correlation matrix
        data = pd.concat([pd.Series(Y_out, name=Y_name), X_out], axis=1)

    # Calculate the correlation matrix
    corr_matrix = data.corr()

    # Set the diagonal elements to NaN to make them white
    np.fill_diagonal(corr_matrix.values, np.nan)

    # Set default values if not already provided in kwargs
    kwargs.setdefault('annot', True)
    kwargs.setdefault('square', True)
    kwargs.setdefault('vmax', 1)
    kwargs.setdefault('vmin', -1)
    kwargs.setdefault('linewidths', 0.5)

    # If cmap is not provided in kwargs, set a default cmap with NaN handling
    if 'cmap' not in kwargs:
        cmap = sns.color_palette("coolwarm", as_cmap=True)
        cmap.set_bad(color='black')  # Make NaN values appear in black
        kwargs['cmap'] = cmap

    # If a subplot is specified, use it; otherwise, create a new figure
    if subplot:
        plt.subplot(*subplot)
    else:
        plt.figure(figsize=(8, 6))

    # Draw the heatmap with specified and default kwargs
    sns.heatmap(corr_matrix, **kwargs)

    # Set main title, x-axis label, and y-axis label
    plt.title(main, fontsize=18)
    plt.xlabel(xlab)
    plt.ylabel(ylab)

    # Rotate the tick labels for readability
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)

    # Show the plot if subplot is not specified
    if subplot is None:
        plt.show()
        plt.clf()
        plt.close()