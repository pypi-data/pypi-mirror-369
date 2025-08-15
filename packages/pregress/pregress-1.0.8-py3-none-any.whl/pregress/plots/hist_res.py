from pregress.modeling.fit import fit
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats  # Import for statistical functions


def hist_res(model, main="Histogram of Residuals", xlab="Residuals", ylab="Density", subplot=None):
    """
    Plots a histogram of the residuals of a fitted statsmodels regression model and overlays a normal distribution curve.

    Args:
        model (statsmodels.regression.linear_model.RegressionResultsWrapper): A fitted statsmodels regression model.
        main (str, optional): Title for the histogram plot.
        xlab (str, optional): Label for the x-axis.
        ylab (str, optional): Label for the y-axis.
        subplot (tuple, optional): A tuple specifying the subplot grid (nrows, ncols, index). If None, a new figure is created.

    Returns:
        None. Displays a histogram of residuals with a normal distribution curve.
    """

    # Calculate residuals
    residuals = model.resid

    # If a subplot is specified, create the subplot; otherwise, create a new figure
    if subplot:
        plt.subplot(*subplot)
    else:
        plt.figure()

    # Plot histogram of the residuals
    plt.hist(residuals, bins=30, color='blue', alpha=0.7, density=True, label='Residuals Histogram')

    # Fit a normal distribution to the residuals
    mu, std = stats.norm.fit(residuals)

    # Create a range of values from the residuals' min to max for plotting the curve
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = stats.norm.pdf(x, mu, std)

    # Plot the normal distribution curve
    plt.plot(x, p, 'k', linewidth=2, label='Normal Distribution')

    # Set title and labels using the new arguments
    plt.title(main)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.legend(loc='upper left')

    # Show the plot only if no subplot is provided
    if subplot is None:
        plt.show()
        plt.clf()
        plt.close()
