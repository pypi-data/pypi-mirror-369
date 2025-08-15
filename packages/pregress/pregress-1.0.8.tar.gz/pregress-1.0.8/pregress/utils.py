# mypackage/utils.py
import pkg_resources
import pandas as pd

def get_data(filename):
    data_path = pkg_resources.resource_filename('pregress', f'data/{filename}')
    return pd.read_csv(data_path)
