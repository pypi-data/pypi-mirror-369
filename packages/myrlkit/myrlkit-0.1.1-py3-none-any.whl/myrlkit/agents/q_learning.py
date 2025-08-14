import numpy as np

class QLearningAgent:
    """Tabular Q-learning agent.

    Parameters
    ----------
    state_size : int
        Number of discrete states.
    action_size : int
        Number of discrete actions.
    alpha : float, default=0.1
        Learning rate.
    gamma : float, default=0.99
        Discount factor.
    epsilon : float, default=0.1
        Exploration rate for epsilon-greedy policy.
    seed : int or None
        RNG seed for reproducibility.
    """

    def __init__(self, state_size, action_size, alpha=0.1, gamma=0.99, epsilon=0.1, seed=None):
        self.state_size = int(state_size)
        self.action_size = int(action_size)
        self.alpha = float(alpha)
        self.gamma = float(gamma)
        self.epsilon = float(epsilon)
        self.rng = np.random.default_rng(seed)
        self.q_table = np.zeros((self.state_size, self.action_size), dtype=float)

    def choose_action(self, state: int) -> int:
        """Choose an action using epsilon-greedy over Q-table."""
        if self.rng.random() < self.epsilon:
            return int(self.rng.integers(self.action_size))
        q_row = self.q_table[state]
        max_q = q_row.max()
        candidates = np.flatnonzero(np.isclose(q_row, max_q))
        return int(self.rng.choice(candidates))

    def update(self, state: int, action: int, reward: float, next_state: int, done: bool):
        """One Q-learning update step."""
        best_next = self.q_table[next_state].max()
        target = reward + (0.0 if done else self.gamma * best_next)
        td_error = target - self.q_table[state, action]
        self.q_table[state, action] += self.alpha * td_error
