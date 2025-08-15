import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.gofplots import ProbPlot
import statsmodels.api as sm
from scipy import stats

def plot_qq(model, conf_level=0.95, subplot=None):
    """
    Generates a QQ plot for the residuals of a fitted statsmodels regression model to assess normality,
    including a confidence band.

    Args:
        model (statsmodels.regression.linear_model.RegressionResultsWrapper): A fitted statsmodels regression model.
        conf_level (float): Confidence level for the confidence band (default is 95%).

    Returns:
        None. Displays a QQ plot of the residuals with a confidence band.
    """
    # Extract residuals
    residuals = model.resid
    n = len(residuals)  # number of observations

    # Create a Probability Plot
    pp = ProbPlot(residuals, fit=True)

    # Generate the QQ plot figure
    fig, ax = plt.subplots(figsize=(6, 4))

    # Generate the QQ plot without explicitly specifying color to avoid redundancy
    qq = pp.qqplot(line='45', alpha=0.5, lw=1, ax=ax)

    # Manually set the color of the line
    ax.get_lines()[1].set_color('red')  # Sets the color of the 45-degree line

    # Generate theoretical quantiles for the QQ plot (normal distribution)
    theoretical_quantiles = np.sort(stats.norm.ppf(np.linspace(0.01, 0.99, n)))
    
    # Generate the lower and upper bounds for the confidence bands
    se = (theoretical_quantiles * np.sqrt((1 - conf_level) / n))  # Standard error for confidence interval
    ci_low = theoretical_quantiles - se
    ci_upp = theoretical_quantiles + se

    # Sort residuals
    sorted_residuals = np.sort(residuals)

    # Fill between the confidence intervals
    ax.fill_between(theoretical_quantiles, ci_low, ci_upp, color='blue', alpha=0.2)

    # Setting the plot title and labels
    ax.set_title('QQ Plot of Residuals with Confidence Band')
    ax.set_xlabel('Theoretical Quantiles')
    ax.set_ylabel('Sample Quantiles')

    # Show the plot if subplot is not specified
    if subplot is None:
        plt.show()
        plt.clf()
        plt.close()
