import os.path

import pandas as pd
from template_ml_model.config import MODEL_OUTPUT_PATH


def load_data(path):
    """
    Load a CSV dataset for training
    """
    df = pd.read_csv(path)
    return df

def load_model(model_file="bandit_values.npy"):
    """
    Load the learned bandit values from training
    """
    import numpy as np
    return np.load(os.path.join(MODEL_OUTPUT_PATH, model_file))