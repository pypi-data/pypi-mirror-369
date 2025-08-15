# handle_included_vars2.py

def handle_included_vars2():
    try:
        x = globals()['x']
        return x
    except KeyError:
        return "Global variable 'x' not found."
