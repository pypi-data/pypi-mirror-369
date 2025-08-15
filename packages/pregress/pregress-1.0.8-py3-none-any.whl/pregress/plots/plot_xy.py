from pregress.modeling.parse_formula import parse_formula
from pregress.modeling.predict import predict
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

def plot_xy(formula, data=None, model=None, pcolor="blue", lcolor="red", xlab=None, ylab=None, title=None, psize=50, subplot=None, alpha=1.0, **kwargs):
    """
    Generates and prints a plot of the regression model fit using a specified formula and data.
    It supports plotting for models with one predictor variable, including potentially nonlinear relationships.
    The function utilizes Seaborn for plotting the scatter plot and Matplotlib for the regression line.

    Args:
        formula (str): Formula to define the model (Y ~ X).
        data (DataFrame, optional): Data frame containing the data.
        model (list, optional): List of fitted statsmodels models or a single fitted model to use for predictions.
        pcolor (str or list, optional): Color of the points in the scatter plot. Can be a single color or a list of colors.
        lcolor (str or list, optional): Color of the regression line(s). Can be a single color or a list of colors corresponding to the models.
        xlab (str, optional): Label for the x-axis.
        ylab (str, optional): Label for the y-axis.
        title (str, optional): Title for the plot.
        psize (int, optional): Size of the points in the scatter plot. Default is 50.
        subplot (tuple, optional): Subplot configuration. Default is None.
        alpha (float, optional): Transparency level for scatter points (0-1). Default is 1.0.
        **kwargs: Additional keyword arguments for customization.

    Returns:
        None. The function creates and shows a plot.
    """
    
    # Clear any existing plots to avoid contamination
    plt.clf()
    plt.cla()
    
    # Parse the formula and ensure the formula includes an intercept
    formula = formula + "+0"
    Y_name, X_names, Y_out, X_out = parse_formula(formula, data)

    # Check the number of predictor variables in the model
    if X_out.shape[1] > 1:
        print("Only one predictor variable can be plotted.")
        return

    # If subplot is specified, create subplot
    if subplot is not None:
        if subplot[2] == 1:  # Check if it's the first subplot
            plt.figure(figsize=(15, 5))  # Specify figure size for better visibility
        plt.subplot(*subplot)

    # Check if pcolor is a list or an array
    if isinstance(pcolor, (list, np.ndarray)):
        unique_colors = np.unique(pcolor)
        legend_labels = kwargs.get('legend_labels', [])
        for i, color in enumerate(unique_colors):
            # Handle case where legend_labels might be shorter than unique_colors
            label = legend_labels[i] if i < len(legend_labels) else None
            sns.scatterplot(x=X_out[pcolor == color].values.flatten(), y=Y_out[pcolor == color], 
                          color=color, s=psize, alpha=alpha, label=label)
    else:
        sns.scatterplot(x=X_out.values.flatten(), y=Y_out, color=pcolor, s=psize, alpha=alpha)

    # If model is a single model, convert it to a list
    if not isinstance(model, list):
        model = [model]

    # If lcolor is a single color, convert it to a list
    if not isinstance(lcolor, list):
        lcolor = [lcolor] * len(model)

    # Plot each model's predictions
    legend_labels = kwargs.get('legend_labels', [])
    for idx, (mdl, color) in enumerate(zip(model, lcolor)):
        # Handle case where legend_labels might be shorter than models
        label = legend_labels[idx] if idx < len(legend_labels) else None
        
        if isinstance(mdl, str) and mdl.lower() in ["line", "l"]:
            # Use regplot for simple linear trend line when explicitly requested
            sns.regplot(x=X_out.values.flatten(), y=Y_out, scatter=False, 
                       line_kws={"color": color, "label": label}, ci=None)
        elif mdl is not None and not isinstance(mdl, str):
            # Generate predictions across the range of X values for fitted models
            X_range = np.linspace(X_out.min(), X_out.max(), 100).reshape(-1, 1)

            # Create prediction DataFrame with consistent variable naming
            # Try to use the original variable name first, then fall back to "X"
            try:
                X_pred = pd.DataFrame({X_names[0]: X_range.flatten()})
                Y_pred = predict(mdl, X_pred)
            except (KeyError, AttributeError):
                # If original variable name doesn't work, try "X"
                try:
                    X_pred = pd.DataFrame({"X": X_range.flatten()})
                    Y_pred = predict(mdl, X_pred)
                except:
                    print(f"Warning: Could not generate predictions for model {idx + 1}")
                    continue

            # Plot the regression line using matplotlib (this will show the logistic curve for logistic models)
            plt.plot(X_range, Y_pred, color=color, lw=2, label=label)
        else:
            print(f"  -> Skipping None model: {repr(mdl)}")

    # Set labels for the x and y axes
    plt.xlabel(xlab if xlab is not None else X_names[0])
    plt.ylabel(ylab if ylab is not None else Y_name)

    # Set the plot title if provided
    if title is not None:
        plt.title(title)

    # Add legend if any labels were provided
    if 'legend_labels' in kwargs and any(kwargs['legend_labels']):
        plt.legend()

    # Show the plot only if subplot is not specified or if it is the last subplot
    # Don't clear/close if we're in subplot mode
    if subplot is None:
        plt.show()
    elif subplot[1] == subplot[2]:  # Last subplot
        plt.tight_layout()  # Adjust layout before showing
        plt.show()
        # Only clear after showing all subplots
        plt.clf()
        plt.close()
