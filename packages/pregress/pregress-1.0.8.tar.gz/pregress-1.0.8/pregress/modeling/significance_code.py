def significance_code(p):
    """Returns the significance code for a given p-value."""
    try:
        p = float(p)
    except ValueError:
        return ''
    if p < 0.001:
        return '***'
    elif p < 0.01:
        return '**'
    elif p < 0.05:
        return '*'
    elif p < 0.1:
        return '.'
    else:
        return ''
