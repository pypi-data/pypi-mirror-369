import numpy as np
import json
from template_ml_model.model import EpsilonGreedyBandit
from template_ml_model.utils import load_model


def predict(context=None, n_trials=10):
    """
    Simulate choosing arms using learned bandit values.

    Args:
        context: Optional dictionary containing contextual features that may influence arm selection
        n_trials: Number of arm selections to make
    """
    bandit_values = load_model("bandit_values.npy")
    n_arms = len(bandit_values)

    # Create a bandit with epsilon=0 (always exploit)
    bandit = EpsilonGreedyBandit(n_arms=n_arms, epsilon=0.0)
    bandit.values = np.array(bandit_values)

    # Adjust values based on context if provided
    if context:
        # Example: Simple feature-based adjustment
        if 'user_segment' in context:
            segment = context['user_segment']
            if segment == 'new':
                # Maybe new users respond better to certain arms
                bandit.values = bandit.values * np.array([1.2, 1.0, 1.0, 0.9, 1.0])
            elif segment == 'returning':
                # Returning users might prefer different arms
                bandit.values = bandit.values * np.array([0.9, 1.1, 1.0, 1.2, 0.8])

    chosen_arms = []
    for _ in range(n_trials):
        arm = bandit.select_arm()
        chosen_arms.append(arm)

    return chosen_arms


if __name__ == "__main__":
    # Example usage with context
    context = {"user_segment": "new"}
    arms = predict(context=context, n_trials=5)
    print("Chosen arms:", arms)