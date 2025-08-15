import matplotlib.pyplot as plt
import statsmodels.api as sm
import numpy as np
from statsmodels.graphics.gofplots import ProbPlot

def plot_cook(model, threshold=0.5, main="Cook's Distance Plot", xlab="Observation Index", ylab="Cook's Distance", subplot=None):
    """
    Plots Cook's Distance for each observation in a fitted statsmodels regression model to identify influential points.

    Args:
        model (statsmodels.regression.linear_model.RegressionResultsWrapper): A fitted statsmodels regression model.
        threshold (float, optional): The threshold for Cook's Distance to highlight influential points. Default is 0.5.
        main (str, optional): Title for the plot.
        xlab (str, optional): Label for the x-axis.
        ylab (str, optional): Label for the y-axis.
        subplot (tuple or None, optional): A tuple specifying the subplot grid (nrows, ncols, index) or None to create a new figure.

    Returns:
        None. Displays a plot of Cook's Distance for each observation.
    """
    # Calculate Cook's Distance
    influence = model.get_influence()
    cooks_d = influence.cooks_distance[0]

    # If a subplot is specified, create the subplot within the given grid; otherwise, create a new figure
    if subplot:
        plt.subplot(*subplot)
    else:
        plt.figure(figsize=(8, 6))

    # Create the plot
    ax = plt.gca()  # Get the current axis (either from subplot or new figure)
    ax.stem(np.arange(len(cooks_d)), cooks_d, markerfmt=",")
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(main)

    # Adding a reference line for the specified threshold
    ax.axhline(y=threshold, linestyle='--', color='red', label=f'Influence threshold ({threshold})')
    ax.legend()

    # Show the plot only if no subplot is provided
    if subplot is None:
        plt.show()
        plt.clf()
        plt.close()
