from pregress.modeling.parse_formula import parse_formula
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm as normal_dist
import warnings


def hists(input_data=None, data=None, bins=30, xcolor="blue", ycolor="red", norm=False, layout="matrix",
          main="Distribution of Variables", xlab=None, ylab="Frequency", subplot=None):
    """
    Generates and prints histograms for all numeric variables specified in the formula or all numeric variables in the DataFrame.

    Args:
        input_data (str or DataFrame): Formula to define the model (dependent ~ independent), a single column name, or a DataFrame containing the data.
        data (DataFrame, optional): Data frame containing the data if a formula is provided.
        bins (int, optional): Number of bins for the histograms.
        xcolor (str, optional): Color of the histograms for the independent variables.
        ycolor (str, optional): Color of the histograms for the dependent variable.
        norm (bool, optional): Whether to include a normal distribution line.
        layout (str, optional): Layout of the histograms - "column", "row", or "matrix".
        main (str, optional): Main title for the plot.
        xlab (str, optional): Label for the x-axis. Defaults to each variable name if not provided.
        ylab (str, optional): Label for the y-axis.
        subplot (tuple, optional): A tuple specifying the subplot grid (nrows, ncols, index).

    Returns:
        None. The function creates and shows histograms.
    """

    # Case 1: Handle single variable input without "~"
    if isinstance(input_data, str) and '~' not in input_data:
        plot_data = pd.DataFrame({input_data: data[input_data]})
        Y_name = None
    # Case 2: Directly given DataFrame
    elif isinstance(input_data, pd.DataFrame):
        plot_data = input_data.select_dtypes(include=[np.number])
        Y_name = None
    # Case 3: Formula provided
    else:
        formula = input_data + "+0"
        Y_name, X_names, Y_out, X_out = parse_formula(formula, data)
        plot_data = pd.concat([pd.Series(Y_out, name=Y_name), X_out], axis=1)

    # Replace infinite values with NaN
    plot_data.replace([np.inf, -np.inf], np.nan, inplace=True)

    num_vars = len(plot_data.columns)

    # Determine the layout
    if layout == "column":
        nrows, ncols = num_vars, 1
    elif layout == "row":
        nrows, ncols = 1, num_vars
    elif layout == "matrix":
        nrows = int(np.ceil(np.sqrt(num_vars)))
        ncols = int(np.ceil(num_vars / nrows))
    else:
        raise ValueError("Invalid layout option. Choose from 'column', 'row', or 'matrix'.")

    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 5 * nrows))
    axes = np.array(axes).reshape(-1)  # Flatten the axes array for easy iteration

    fig.suptitle(main)  # Set the main title for the entire figure

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)

        for i, var in enumerate(plot_data.columns):
            ax = axes[i]
            color = ycolor if var == Y_name else xcolor
            sns.histplot(plot_data[var], bins=bins, kde=False, color=color, ax=ax, edgecolor='black')

            if norm:
                mean = plot_data[var].mean()
                std = plot_data[var].std()
                x = np.linspace(plot_data[var].min(), plot_data[var].max(), 100)
                p = normal_dist.pdf(x, mean, std)
                ax.plot(x, p * (len(plot_data[var]) * np.diff(np.histogram(plot_data[var], bins=30)[1])[0]), 'k',
                        linewidth=2)

            # Set individual titles and labels using provided arguments
            ax.set_title(f'Histogram of {var}')
            ax.set_xlabel(xlab if xlab else var)
            ax.set_ylabel(ylab)

        # Remove any unused subplots in the matrix layout
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout with space for the main title

        # Show the plot if subplot is not specified
        if subplot is None:
            plt.show()
            plt.clf()
            plt.close()
