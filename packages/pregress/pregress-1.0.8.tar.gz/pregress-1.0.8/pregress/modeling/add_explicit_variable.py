from .extract_variable import extract_variable
from .apply_transformation import apply_transformation
import pandas as pd
from functools import reduce

def add_explicit_variable(df, X_vars, predictor, additional_globals=None):
    """Process and add variables to the dictionary, handling categorical interactions."""
    trans, untransformed = extract_variable(predictor)

    if trans == 'interaction':
        interaction_parts = untransformed.split(':')
        transformed_parts = []

        for part in interaction_parts:
            part_trans, part_var = extract_variable(part)
            if df[part_var].dtype.kind in 'O' or df[part_var].dtype.name == 'category':
                dummies = pd.get_dummies(df[part_var], prefix=part_var)
                for dummy_col in dummies.columns:
                    transformed_parts.append(apply_transformation(dummies[dummy_col], part_trans))
            else:
                transformed_parts.append(apply_transformation(df[part_var], part_trans))

        combined_interaction = reduce(lambda x, y: x * y, transformed_parts)
        X_vars[predictor] = combined_interaction
    else:
        if untransformed in df.columns:
            X_vars[predictor] = apply_transformation(df[untransformed], trans)
        else:
            raise ValueError(f"The variable '{untransformed}' is not available in the DataFrame.")

