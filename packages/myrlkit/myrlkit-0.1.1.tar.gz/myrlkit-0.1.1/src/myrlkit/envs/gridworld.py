import numpy as np
from typing import List, Tuple, Optional, Dict

class GridWorld:
    """Small deterministic grid world with 4 actions: up, right, down, left.

    States are flattened indices: s = y * width + x.
    Reward: -1 per step, +0 on obstacles (blocked), +10 at goal, episode terminates at goal.
    """

    ACTIONS = [(0,-1), (1,0), (0,1), (-1,0)]  # U, R, D, L

    def __init__(self, width: int, height: int, start: Tuple[int,int]=(0,0), goal: Tuple[int,int]=(3,3),
                 obstacles: Optional[List[Tuple[int,int]]] = None, seed=None):
        self.width = int(width)
        self.height = int(height)
        self.n_states = self.width * self.height
        self.n_actions = 4
        self.start_xy = tuple(start)
        self.goal_xy = tuple(goal)
        self.obstacles = set(obstacles or [])
        self.rng = np.random.default_rng(seed)
        self._xy = self.start_xy

    def reset(self) -> int:
        self._xy = self.start_xy
        return self._to_state(self._xy)

    def step(self, action: int):
        dx, dy = self.ACTIONS[action]
        nx, ny = self._xy[0] + dx, self._xy[1] + dy

        # Stay in bounds
        nx = min(max(nx, 0), self.width - 1)
        ny = min(max(ny, 0), self.height - 1)

        if (nx, ny) in self.obstacles:
            # Bump into obstacle, no move, small penalty
            reward = -1.0
            done = False
            next_xy = self._xy
        else:
            next_xy = (nx, ny)
            if next_xy == self.goal_xy:
                reward = 10.0
                done = True
            else:
                reward = -1.0
                done = False

        self._xy = next_xy
        return self._to_state(next_xy), reward, done, {}

    def _to_state(self, xy) -> int:
        return xy[1] * self.width + xy[0]

    def _from_state(self, s: int):
        x = s % self.width
        y = s // self.width
        return (x, y)

    def render_policy(self, q_table):
        """Return an ASCII arrow map for the greedy policy."""
        arrows = {0:"↑", 1:"→", 2:"↓", 3:"←"}
        grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if (x,y) in self.obstacles:
                    row.append("■")
                elif (x,y) == self.goal_xy:
                    row.append("G")
                else:
                    s = self._to_state((x,y))
                    a = int(np.argmax(q_table[s]))
                    row.append(arrows[a])
            grid.append(" ".join(row))
        return "\n".join(grid)
