import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import boxcox, boxcox_llf

def box_cox(model):
    y = model.model.endog
    if np.any(y <= 0):
        raise ValueError("All values in the response variable must be positive for Box-Cox transformation.")

    y_transformed, fitted_lambda = boxcox(y)

    # Calculate lambdas from -3 to 3 for better CI accuracy
    lambdas = np.linspace(-3, 3, 100)
    log_likelihood = [boxcox_llf(lmbda, y) for lmbda in lambdas]

    # Plot lambdas from -2.1 to 2.1
    plot_lambdas = lambdas[(lambdas >= -2.1) & (lambdas <= 2.1)]
    plot_log_likelihood = [boxcox_llf(lmbda, y) for lmbda in plot_lambdas]

    max_log_likelihood = boxcox_llf(fitted_lambda, y)
    ci_cutoff = max_log_likelihood - 1.92  # Chi-squared distribution cutoff for 95% CI (1 degree of freedom)
    ci_lambdas = lambdas[np.array(log_likelihood) >= ci_cutoff]

    plt.figure(figsize=(10, 6))

    # Plot the restricted range of log-likelihood from -2.1 to 2.1
    plt.plot(plot_lambdas, plot_log_likelihood, label='Log-Likelihood Function')

    # Set xlim to focus on the typical range of -2 to 2
    plt.xlim([-2, 2])

    # Set ylim based exactly on the min and max log-likelihood without additional padding
    plt.ylim([min(plot_log_likelihood), max(plot_log_likelihood)+.05* (max(plot_log_likelihood) - min(plot_log_likelihood))])

    if -2 <= fitted_lambda <= 2:
        lambda_lower = ci_lambdas[0]
        lambda_upper = ci_lambdas[-1]
        plt.axvline(lambda_lower, color='b', linestyle='--', label=f'95% CI Lower: {lambda_lower:.4f}')
        plt.axvline(fitted_lambda, color='r', linestyle='--', label=f'Best Lambda: {fitted_lambda:.4f}')
        plt.axvline(lambda_upper, color='b', linestyle='--', label=f'95% CI Upper: {lambda_upper:.4f}')
    else:
        print(f"The fitted_lambda is {fitted_lambda:.4f}, which is outside the typical range of -2 to 2. CI lines not plotted.")
        
    plt.xlabel('Lambda')
    plt.ylabel('Log-Likelihood')
    plt.title('Log-Likelihood for Box-Cox Transformation')
    plt.legend(loc='lower right')
    plt.grid(True)
    plt.show()
