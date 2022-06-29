"""Example policy for Real Robot Challenge 2022"""
import numpy as np
import torch

from rrc_2022_datasets import PolicyBase

from . import policies


# FIXME: this policy is not following the PolicyBase interface and is returning position
# commands
class MyPolicy:
    def __init__(self, steps=1000):
        position_up = np.array([0.5, 1.2, -2.4] * 3)
        position_down = np.array([-0.08, 0.84, -1.2] * 3)
        trajectory_range = position_up - position_down
        # steps = 1000
        step_size = trajectory_range / steps

        self.trajectory = [position_down + i * step_size for i in range(steps)]
        self.i = 0

    def reset(self):
        pass  # nothing to do here

    def get_action(self, observation):
        if self.i >= len(self.trajectory):
            # reverse trajectory
            self.trajectory = self.trajectory[::-1]
            self.i = 0

        target_position = self.trajectory[self.i]
        self.i += 1

        # TODO: should be changed to return torques instead of positions
        return target_position


class TorchBasePolicy(PolicyBase):
    def __init__(
        self,
        torch_model_path,
        action_space,
        observation_space,
        episode_length,
    ):
        self.action_space = action_space
        self.device = "cpu"

        # load torch script
        self.policy = torch.jit.load(
            torch_model_path, map_location=torch.device(self.device)
        )
        self.action_space = action_space

    @staticmethod
    def is_using_flattened_observations():
        return True

    def reset(self):
        pass  # nothing to do here

    def get_action(self, observation):
        observation = torch.tensor(observation, dtype=torch.float, device=self.device)
        action = self.policy(observation.unsqueeze(0))
        action = action.detach().numpy()[0]
        action = np.clip(action, self.action_space.low, self.action_space.high)
        return action


class TorchPushPolicy(TorchBasePolicy):
    """Example policy for the push task, using a torch model to provide actions.

    Expects flattened observations.
    """

    def __init__(self, action_space, observation_space, episode_length):
        model = policies.get_model_path("push.pt")
        super().__init__(
            model, action_space, observation_space, episode_length
        )


class TorchLiftPolicy(TorchBasePolicy):
    """Example policy for the lift task, using a torch model to provide actions.

    Expects flattened observations.
    """

    def __init__(self, action_space, observation_space, episode_length):
        model = policies.get_model_path("lift.pt")
        super().__init__(
            model, action_space, observation_space, episode_length
        )
