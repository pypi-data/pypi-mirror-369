import numpy as np

from template_ml_model.model import EpsilonGreedyBandit


def predict(bandit_values, n_trials=10):
    """
    Simulate choosing arms using learned bandit values.
    """
    n_arms = len(bandit_values)
    # Create a bandit with epsilon=0 (always exploit)
    bandit = EpsilonGreedyBandit(n_arms=n_arms, epsilon=0.0)
    bandit.values = np.array(bandit_values)

    chosen_arms = []
    for _ in range(n_trials):
        arm = bandit.select_arm()
        chosen_arms.append(arm)

    return chosen_arms

if __name__ == "__main__":
    # Example: learned values from training
    learned_values = [0.6, 0.4, 0.2, 0.8, 0.1]
    arms = predict(learned_values, n_trials=5)
    print("Chosen arms:", arms)