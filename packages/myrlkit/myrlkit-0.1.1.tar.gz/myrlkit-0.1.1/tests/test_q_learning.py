import numpy as np
from myrlkit.agents import QLearningAgent
from myrlkit.envs import GridWorld

def test_q_learning_runs():
    env = GridWorld(width=3, height=3, start=(0,0), goal=(2,2), seed=0)
    agent = QLearningAgent(state_size=env.n_states, action_size=env.n_actions, alpha=0.5, gamma=0.9, epsilon=0.2, seed=0)
    s = env.reset()
    for _ in range(50):
        a = agent.choose_action(s)
        ns, r, done, _ = env.step(a)
        agent.update(s, a, r, ns, done)
        s = ns
        if done:
            break
    assert agent.q_table.shape == (env.n_states, env.n_actions)
