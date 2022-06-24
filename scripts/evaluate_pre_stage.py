"""Evaluate a policy in simulation (used for the pre-stage)."""
import argparse
import importlib
import json
import logging
import pathlib
import typing

import gym

from rrc_2022_datasets import Evaluation, PolicyBase, TriFingerDatasetEnv


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
    except Exception:
        raise RuntimeError(
            "Failed to import policy %s from module %s" % (class_name, module_name)
        )

    return Policy


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "policy_class",
        type=str,
        help="Name of the policy class (something like 'package.module.Class').",
    )
    parser.add_argument(
        "--env-name",
        type=str,
        default="trifinger-cube-push-sim-expert-v0",
        help="Name of the gym environment to load.",
    )
    parser.add_argument(
        "--no-visualization",
        action="store_true",
        help="Disable visualization of environment.",
    )
    parser.add_argument(
        "--n-episodes",
        type=int,
        default=64,
        help="Number of episodes to run.",
    )
    parser.add_argument(
        "--structured-observations",
        action="store_true",
        help="""Provide observation as a structured dictionary instead of a flattened
            array.
        """,
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        metavar="FILENAME",
        help="Save results to a JSON file.",
    )
    args = parser.parse_args()

    Policy = load_policy_class(args.policy_class)

    env = typing.cast(
        TriFingerDatasetEnv,
        gym.make(
            args.env_name,
            disable_env_checker=True,
            visualization=not args.no_visualization,
            flatten_obs=not args.structured_observations,
        ),
    )

    policy = Policy(env.action_space, env.observation_space, env.sim_env.episode_length)

    evaluation = Evaluation(env)
    eval_res = evaluation.evaluate(
        policy=policy,
        n_episodes=args.n_episodes,
    )
    json_result = json.dumps(eval_res, indent=4)

    print("Evaluation result: ")
    print(json_result)

    if args.output:
        args.output.write_text(json_result)
