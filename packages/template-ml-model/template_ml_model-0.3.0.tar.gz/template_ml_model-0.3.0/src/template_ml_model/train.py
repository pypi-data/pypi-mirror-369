import argparse
import os
import numpy as np

from template_ml_model.config import DATASET_CHANNEL_PATH, MODEL_OUTPUT_PATH
from template_ml_model.model import EpsilonGreedyBandit
from template_ml_model.utils import load_data


def train():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_arms", type=int, default=5)
    parser.add_argument("--epsilon", type=float, default=0.1)
    parser.add_argument("--data_dir", type=str, default=os.environ.get("DATASET_CHANNEL_PATH"))
    args = parser.parse_args()

    # Load dataset
    data_path = os.path.join(DATASET_CHANNEL_PATH, "dataset.csv")
    df = load_data(data_path)

    # Initialize bandit
    bandit = EpsilonGreedyBandit(n_arms=args.num_arms, epsilon=args.epsilon)

    # Simulate training (loop through rows)
    for _, row in df.iterrows():
        chosen_arm = bandit.select_arm()
        reward = row[f"arm_{chosen_arm}"]
        bandit.update(chosen_arm, reward)

    model_path = os.path.join(MODEL_OUTPUT_PATH, "bandit_values.npy")
    np.save(model_path, bandit.values)

    print("Training finished. Learned values:", bandit.values)
    print(f"Model saved to {model_path}")


if __name__ == "__main__":
    train()
