import pandas as pd

def load_data(path):
    """
    Load a CSV dataset for training
    """
    df = pd.read_csv(path)
    return df