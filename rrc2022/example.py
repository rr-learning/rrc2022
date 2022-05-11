"""Example policy for Real Robot Challenge 2022"""
import numpy as np


class MyPolicy:
    def __init__(self, steps=1000):
        position_up = np.array([0.5, 1.2, -2.4] * 3)
        position_down = np.array([-0.08, 0.84, -1.2] * 3)
        trajectory_range = position_up - position_down
        # steps = 1000
        step_size = trajectory_range / steps

        self.trajectory = [position_down + i * step_size for i in range(steps)]
        self.i = 0

    def get_action(self, observation):
        if self.i >= len(self.trajectory):
            # reverse trajectory
            self.trajectory = self.trajectory[::-1]
            self.i = 0

        target_position = self.trajectory[self.i]
        self.i += 1

        # TODO: should be changed to return torques instead of positions
        return target_position
