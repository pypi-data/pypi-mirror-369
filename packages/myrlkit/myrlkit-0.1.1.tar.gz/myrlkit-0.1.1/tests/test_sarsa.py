import numpy as np
from myrlkit.agents import SARSAAgent
from myrlkit.envs import GridWorld

def test_sarsa_runs():
    env = GridWorld(width=3, height=3, start=(0,0), goal=(2,2), seed=0)
    agent = SARSAAgent(state_size=env.n_states, action_size=env.n_actions, alpha=0.5, gamma=0.9, epsilon=0.2, seed=0)
    s = env.reset()
    a = agent.choose_action(s)
    for _ in range(50):
        ns, r, done, _ = env.step(a)
        na = agent.choose_action(ns)
        agent.update(s, a, r, ns, na, done)
        s, a = ns, na
        if done:
            break
    assert agent.q_table.shape == (env.n_states, env.n_actions)
