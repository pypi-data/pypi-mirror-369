# handle_included_vars.py

from .add_explicit_variable import add_explicit_variable

def handle_included_vars(df, included_vars, excluded_vars, untransformed_Y):
    """
    Processes included variables to apply any necessary transformations and exclude specified variables.
    """
    X_vars = {}
    included_columns = [col for col in df.columns if col != untransformed_Y and col not in excluded_vars]

    # Handle the '.' operator
    if '.' in included_vars or '(.)' in included_vars:
        for col in included_columns:
            X_vars[col] = df[col]

    # Handle the '.^2' or '(.)^2' operator
    if '.^2' in included_vars or '(.)^2' in included_vars:
        for i in range(len(included_columns)):
            for j in range(i, len(included_columns)):
                col1 = included_columns[i]
                col2 = included_columns[j]
                if i == j:
                    # Include the column if both indices are the same
                    X_vars[col1] = df[col1]
                else:
                    # Create interaction term squared for distinct column pairs
                    interaction_term = f'{col1}:{col2}'
                    X_vars[interaction_term] = (df[col1] * df[col2])

    # Handle explicitly listed variables
    for predictor in included_vars:
        if predictor not in {'.', '(.)', '.^2', '(.)^2'}:
            add_explicit_variable(df, X_vars, predictor)

    return X_vars
