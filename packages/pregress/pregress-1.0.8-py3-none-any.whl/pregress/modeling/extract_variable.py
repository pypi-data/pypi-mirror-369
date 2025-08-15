import re

def extract_variable(text):
    # Handle interactions specified like 'X1:X2'.
    if ':' in text:
        vars = text.split(':')
        interaction_term = ':'.join(vars)
        return 'interaction', interaction_term

    # Regex to find function-based transformations like 'log(X)'.
    function_match = re.search(r'(\w+)\(([\w\.]+)\)', text)
    if function_match:
        trans, var = function_match.groups()
        return trans, var

    # Handle exponentiations directly specified like 'X^2', 'X^.5', or 'X^(.5)'
    exp_match = re.search(r'([\w\.]+)\^\(?(\d*\.?\d+)\)?', text)
    if exp_match:
        var, exp = exp_match.groups()
        return f'power_{exp}', var

    # Handle inverse transformations specified like '1/X'.
    inv_match = re.search(r'1/([\w\.]+)', text)
    if inv_match:
        var = inv_match.group(1)
        return 'inverse', var

    # Check if the text is just a variable name (no transformations)
    if re.match(r'^\w+$', text):
        return 'identity', text

    # If text format is unknown or unsupported
    raise ValueError(f"Unsupported format or unknown transformation in text: '{text}'")
