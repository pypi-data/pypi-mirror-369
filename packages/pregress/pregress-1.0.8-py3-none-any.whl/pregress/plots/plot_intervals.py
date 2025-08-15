import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
from pregress.modeling.intervals import intervals

def plot_intervals(model, newX, interval='confidence', level=0.95, xlab=None, ylab=None, main=None, subplot=None):
    """
    Plot confidence or prediction intervals for a statsmodels object.

    Parameters:
    model : statsmodels object
        The fitted statsmodels model.
    newX : DataFrame
        A vector (1 observation) of predictor variables if num_predictors > 1.
    interval : str
        Type of interval to calculate, either 'confidence' or 'prediction'.
    level : float
        The confidence level for the intervals. Default is 0.95.
    xlab : str, optional
        Label for the x-axis.
    ylab : str, optional
        Label for the y-axis.
    main : str, optional
        Title for the plot.
    subplot : optional
        Subplot configuration.
    """
    # Calculate the intervals using the intervals function
    interval_data = intervals(model, newX, interval=interval, level=level)
    
    non_constant_cols = [col for col in newX.columns if not np.all(newX[col] == 1)]
    num_predictors = len(non_constant_cols)

    if num_predictors == 1:
        # Single predictor case: plot response vs predictor
        predictor = newX[non_constant_cols[0]]
        xlab = xlab if xlab else non_constant_cols[0]
        ylab = ylab if ylab else 'Response'
        main = main if main else f'Regression Line with {int(level*100)}% Interval'
        
        plt.figure(figsize=(10, 6))
        plt.plot(predictor, model.predict(newX), label='Regression Line', color='blue')
        plt.fill_between(predictor, interval_data['Lower Bound'], interval_data['Upper Bound'], color='gray', alpha=0.2)
        plt.plot(predictor, interval_data['Lower Bound'], 'r--', label=f'{int(level*100)}% Interval')
        plt.plot(predictor, interval_data['Upper Bound'], 'r--')
        plt.title(main)
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        plt.legend(loc='upper right')
        plt.grid(True)

    else:
        # Multiple predictors case: Ensure newX is a vector (one observation)
        if newX.shape[0] != 1:
            raise ValueError("newX must be a vector (one observation) when there are multiple predictors.")

        xlab = xlab if xlab else 'Response'
        main = main if main else f'{int(level*100)}% Interval for the Observation'
        
        # Extract the prediction and bounds for this observation
        prediction = interval_data['Prediction'].iloc[0]
        lower_bound = interval_data['Lower Bound'].iloc[0]
        upper_bound = interval_data['Upper Bound'].iloc[0]

        # Plot the PDF of the response with bounds
        plt.figure(figsize=(10, 6))
        mu, std = prediction, (upper_bound - lower_bound) / 4  # Approximate std
        x = np.linspace(mu - 3 * std, mu + 3 * std, 100)
        pdf = norm.pdf(x, mu, std)

        plt.plot(x, pdf, label='Density', color='blue')
        plt.axvline(mu, color='blue', linestyle='--', label='Prediction')
        plt.axvline(lower_bound, color='red', linestyle='--', label=f'{int(level*100)}% Interval')
        plt.axvline(upper_bound, color='red', linestyle='--')
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
