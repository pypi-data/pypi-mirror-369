import pandas as pd
from .parse_formula import parse_formula
from pregress.plots.barplot import barplot
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.preprocessing import StandardScaler

def vif(formula=None, data=None, plot=False, xlab='Predictor', ylab='VIF Value', title='Variance Inflation Factors', ascending=True):
    if isinstance(data, dict):
        data = pd.DataFrame(data)

    if formula:
        formula = formula + '+0'
        _, _, _, X = parse_formula(formula, data)
    else:
        X = data

    # Standardize the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Calculate VIF for each predictor
    vif_values = [variance_inflation_factor(X_scaled, i) for i in range(X_scaled.shape[1])]

    # Create a DataFrame with feature names as column headers
    vif_data = pd.DataFrame([vif_values], columns=X.columns)

    # Sort the VIF values if required
    vif_data = vif_data.T
    vif_data.columns = ['VIF']
    vif_data = vif_data.sort_values(by='VIF', ascending=ascending)

    if plot:
        barplot(data=vif_data.T, ylab=ylab, xlab=xlab, title=title)

    return vif_data.T
