import numpy as np

class EpsilonGreedyBandit:
    """Epsilon-greedy agent for K-armed bandits."""

    def __init__(self, k: int, epsilon: float = 0.1, seed=None):
        self.k = int(k)
        self.epsilon = float(epsilon)
        self.rng = np.random.default_rng(seed)
        self.counts = np.zeros(self.k, dtype=int)
        self.q_estimates = np.zeros(self.k, dtype=float)

    def select_action(self) -> int:
        if self.rng.random() < self.epsilon:
            return int(self.rng.integers(self.k))
        max_q = self.q_estimates.max()
        candidates = np.flatnonzero(np.isclose(self.q_estimates, max_q))
        return int(self.rng.choice(candidates))

    def update(self, action: int, reward: float):
        self.counts[action] += 1
        n = self.counts[action]
        self.q_estimates[action] += (reward - self.q_estimates[action]) / n
