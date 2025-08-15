import pandas as pd
import statsmodels.api as sm
from .extract_variable import extract_variable
from .apply_transformation import apply_transformation

def predict(model, newX=None, method='ols', dummies = True):
    """
    This function takes a regression model object and a new set of predictor variables,
    and returns the predictions. The default model type is statsmodels.

    Parameters:
    model: The fitted regression model (default is statsmodels).
    newX (pandas.DataFrame or numpy.ndarray, optional): The new predictor variables.
    type (str): The type of model, default is 'statsmodels'.

    Returns:
    numpy.ndarray: The predicted values.
    """
    if method.lower() == 'ols':
        # Step 1: Check if newX is provided; if not, return the fitted values from the model
        if newX is None:
            return model.fittedvalues

        # Step 2: Convert newX to a DataFrame if it is not already one
        if not isinstance(newX, pd.DataFrame):
            newX = pd.DataFrame(newX)
        
        # Step 2.5: Extract Dummies
        if dummies:
            newX = pd.get_dummies(newX, drop_first=True)
            # Convert binary variables (True/False) to numeric (0/1)
            binary_columns = newX.select_dtypes(include=['bool']).columns
            newX[binary_columns] = newX[binary_columns].astype(int)
            
        # Step 3: Extract the names of the model's predictor variables
        model_columns = model.model.exog_names

        # Step 4: Identify and extract any necessary transformations for each predictor variable
        transformations = {}
        for col in model_columns:
            if col != 'Intercept':
                transformations[col] = extract_variable(col)

        # Step 5: Initialize a new DataFrame to hold transformed values
        transformed_X = pd.DataFrame(index=newX.index)

        # Step 6: Apply the extracted transformations to newX and handle interaction terms
        for col, info in transformations.items():
            transform_type, variable = info
            if transform_type == 'interaction':
                variables = variable.split(':')
                interaction_term = newX[variables[0]]
                for var in variables[1:]:
                    interaction_term *= newX[var]
                transformed_X[col] = interaction_term
            else:
                transformed_X[col] = apply_transformation(newX[variable], transform_type)

        # Step 7: Add a constant column for the intercept to transformed_X if the model includes an intercept
        if 'Intercept' in model_columns:
            transformed_X['Intercept'] = 1
        if 'const' in model_columns:
            transformed_X['const'] = 1
            
        # Step 8: Ensure transformed_X contains all required columns for prediction and raise an error if any are missing
        missing_cols = set(model_columns) - set(transformed_X.columns)
        if missing_cols:
            raise ValueError(f"The following required columns are missing from transformed_X: {missing_cols}")

        # Step 9: Ensure columns are in the correct order
        transformed_X = transformed_X[model_columns]
        
        # Step 10: Use the transformed_X to generate and return predictions from the model
        predictions = model.predict(transformed_X)

        return predictions

    else:
        raise ValueError(f"Model type '{type}' is not supported.")
