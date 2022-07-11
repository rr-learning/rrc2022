"""Validate policy (check if interface is correct).

Tries to import the specified policy, instantiate it and send a random observation to
verify if the returned action is valid.

This script is used by validate.py.  See there for more information.
"""
import argparse
import importlib
import logging
import sys
import typing

import gym

from rrc_2022_datasets import PolicyBase, TriFingerDatasetEnv


def load_policy_class(policy_class_str: str) -> typing.Type[PolicyBase]:
    """Import the given policy class

    Args:
        The name of the policy class in the format "package.module.Class".

    Returns:
        The specified policy class.

    Raises:
        RuntimeError: If importing of the class fails.
    """
    try:
        module_name, class_name = policy_class_str.rsplit(".", 1)
        logging.info("import %s from %s" % (class_name, module_name))
        module = importlib.import_module(module_name)
        Policy = getattr(module, class_name)
    except Exception as e:
        raise RuntimeError(
            "Failed to import policy %s from module %s. Error message: %s"
            % (class_name, module_name, e)
        )

    return Policy


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "task",
        type=str,
        choices=["push", "lift"],
        help="Which task to evaluate ('push' or 'lift').",
    )
    parser.add_argument(
        "policy_class",
        type=str,
        help="Name of the policy class (something like 'package.module.Class').",
    )
    args = parser.parse_args()

    if args.task == "push":
        env_name = "trifinger-cube-push-sim-expert-v0"
    elif args.task == "lift":
        env_name = "trifinger-cube-lift-sim-expert-v0"
    else:
        print("Invalid task %s" % args.task)
        return 1

    try:
        Policy = load_policy_class(args.policy_class)
    except Exception as e:
        print(e)
        return 1

    flatten_observations = Policy.is_using_flattened_observations()
    if flatten_observations:
        print("Using flattened observations")
    else:
        print("Using structured observations")

    env = typing.cast(
        TriFingerDatasetEnv,
        gym.make(
            env_name,
            disable_env_checker=True,
            visualization=False,
            flatten_obs=flatten_observations,
        ),
    )

    policy = Policy(env.action_space, env.observation_space, env.sim_env.episode_length)
    policy.reset()

    # sample random observation
    observation = env.observation_space.sample()

    action = policy.get_action(observation)

    if not env.action_space.contains(action):
        print("ERROR: invalid action")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
