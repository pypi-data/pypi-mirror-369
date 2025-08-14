import numpy as np

class KArmedBandit:
    """Stationary K-armed Gaussian bandit."""

    def __init__(self, k: int = 10, means=None, std: float = 1.0, seed=None):
        self.k = int(k)
        self.rng = np.random.default_rng(seed)
        if means is None:
            means = self.rng.normal(loc=0.0, scale=1.0, size=self.k)
        self.means = np.array(means, dtype=float)
        self.std = float(std)

    def pull(self, action: int) -> float:
        return float(self.rng.normal(self.means[action], self.std))
