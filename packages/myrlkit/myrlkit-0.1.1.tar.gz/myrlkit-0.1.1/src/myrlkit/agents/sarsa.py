import numpy as np

class SARSAAgent:
    """Tabular SARSA (on-policy TD control) agent."""

    def __init__(self, state_size, action_size, alpha=0.1, gamma=0.99, epsilon=0.1, seed=None):
        self.state_size = int(state_size)
        self.action_size = int(action_size)
        self.alpha = float(alpha)
        self.gamma = float(gamma)
        self.epsilon = float(epsilon)
        self.rng = np.random.default_rng(seed)
        self.q_table = np.zeros((self.state_size, self.action_size), dtype=float)

    def _eps_greedy(self, state: int) -> int:
        if self.rng.random() < self.epsilon:
            return int(self.rng.integers(self.action_size))
        q_row = self.q_table[state]
        max_q = q_row.max()
        candidates = np.flatnonzero(np.isclose(q_row, max_q))
        return int(self.rng.choice(candidates))

    def choose_action(self, state: int) -> int:
        return self._eps_greedy(state)

    def update(self, state: int, action: int, reward: float, next_state: int, next_action: int, done: bool):
        target = reward + (0.0 if done else self.gamma * self.q_table[next_state, next_action])
        td_error = target - self.q_table[state, action]
        self.q_table[state, action] += self.alpha * td_error
