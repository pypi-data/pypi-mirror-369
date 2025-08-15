import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy.stats import norm

def plot_interval(model, newX, interval='confidence', observation=None, level=0.95, xlab=None, ylab=None, main=None, subplot=None):
    """
    Plot confidence or prediction intervals for a statsmodels object.

    Parameters:
    model : statsmodels object
        The fitted statsmodels model.
    newX : DataFrame
        DataFrame of predictor variables.
    interval : str
        Type of interval to calculate, either 'confidence' or 'prediction'.
    observation : int, optional
        Observation number to plot the PDF for multiple predictors. Required if newX has multiple predictors.
    level : float
        The confidence level for the intervals. Default is 0.95.
    xlab : str, optional
        Label for the x-axis.
    ylab : str, optional
        Label for the y-axis.
    main : str, optional
        Title for the plot.

    Returns:
    intervals : DataFrame
        DataFrame with lower bound, prediction, and upper bound.
    """
    # Ensure newX is a DataFrame and align its columns with the model's parameters
    if not isinstance(newX, pd.DataFrame):
        newX = pd.DataFrame(newX)

    model_params = model.params.index
    intercept_name = None
    for term in model_params:
        if term.lower() in ['const', 'intercept']:
            intercept_name = term
            break

    if intercept_name and intercept_name not in newX.columns:
        newX.insert(0, intercept_name, 1)

    newX = newX[model_params]  # Ensure newX columns are in the same order as model parameters

    if interval not in ['confidence', 'prediction']:
        raise ValueError("Interval must be 'confidence' or 'prediction'")

    preds = model.get_prediction(newX)
    alpha = 1 - level
    summary_frame = preds.summary_frame(alpha=alpha)

    if interval == 'confidence':
        lower_bound = summary_frame['mean_ci_lower']
        upper_bound = summary_frame['mean_ci_upper']
    elif interval == 'prediction':
        lower_bound = summary_frame['obs_ci_lower']
        upper_bound = summary_frame['obs_ci_upper']

    prediction = summary_frame['mean']

    intervals = pd.DataFrame({
        'Lower Bound': lower_bound,
        'Prediction': prediction,
        'Upper Bound': upper_bound
    })

    # Determine the number of predictor variables (excluding any constant column)
    non_constant_cols = [col for col in newX.columns if not np.all(newX[col] == 1)]
    num_predictors = len(non_constant_cols)

    if num_predictors == 1:
        # Plot response vs predictor
        predictor = newX[non_constant_cols[0]]
        xlab = xlab if xlab else non_constant_cols[0]
        ylab = ylab if ylab else 'Response'
        main = main if main else f'Regression Line with {int(level*100)}% {interval.capitalize()} Interval'
        plt.figure(figsize=(10, 6))
        plt.plot(predictor, model.predict(newX), label='Regression Line', color='blue')
        plt.fill_between(predictor, lower_bound, upper_bound, color='gray', alpha=0.2)
        plt.plot(predictor, lower_bound, 'r--', label=f'{int(level*100)}% {interval.capitalize()} Interval')
        plt.plot(predictor, upper_bound, 'r--')
        plt.title(main)
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        # Dynamically determine legend position
        legend_loc = 'upper right' if model.predict(newX).mean() > np.median(model.predict(newX)) else 'upper left'
        plt.legend(loc=legend_loc)
        plt.grid(True)
        
        # Show the plot if subplot is not specified
        if subplot is None:
            plt.show()
            plt.clf()
            plt.close()
    else:
        if observation is None:
            raise ValueError("An observation number must be specified for multiple predictors")

        # Plot the PDF of the response with bounds for the specified observation
        xlab = xlab if xlab else 'Response'
        main = main if main else f'{int(level*100)}% {interval.capitalize()} Interval for Observation {observation+1}'
        plt.figure(figsize=(10, 6))
        mu, std = prediction[observation], (upper_bound[observation] - lower_bound[observation]) / 4  # Approximation
        x = np.linspace(mu - 3*std, mu + 3*std, 100)
        pdf = norm.pdf(x, mu, std)
        plt.plot(x, pdf, label='Density', color='blue')
        plt.axvline(mu, color='blue', linestyle='--', label='Prediction')
        plt.axvline(lower_bound[observation], color='red', linestyle='--', label=f'{int(level*100)}% {interval.capitalize()} Interval')
        plt.axvline(upper_bound[observation], color='red', linestyle='--')
        plt.fill_between(x, pdf, color='gray', alpha=0.2)
        plt.title(main)
        plt.xlabel(xlab)
        plt.ylabel('Density')
        plt.legend(loc='upper right')
        plt.grid(True)
        
        # Show the plot if subplot is not specified
        if subplot is None:
            plt.show()
            plt.clf()
            plt.close()

    return intervals
