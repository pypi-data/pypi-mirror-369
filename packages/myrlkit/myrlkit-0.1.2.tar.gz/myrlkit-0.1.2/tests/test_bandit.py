import numpy as np
from myrlkit.agents import EpsilonGreedyBandit
from myrlkit.envs import KArmedBandit

def test_bandit_runs():
    env = KArmedBandit(k=5, seed=0)
    agent = EpsilonGreedyBandit(k=env.k, epsilon=0.1, seed=0)
    for _ in range(100):
        a = agent.select_action()
        r = env.pull(a)
        agent.update(a, r)
    assert agent.counts.sum() == 100
