#!/usr/bin/env python3
"""Validate package and policy structure.

Performs a number of checks to verify that the specified package is set up correctly and
the configured policy follows the required interface needed to run jobs on the robot.

It is recommended to run this script before submitting jobs to the robot to rule out
some basic errors (e.g. because the policy cannot be imported or does not follow the
required interface).

Ideally run it inside the Apptainer image like this:

    cd path/to/your_package
    apptainer run -e --bind=$(pwd) rrc2022.sif python3 validate.py

Replace `rrc2022.sif` accordingly, if using a custom container.
"""
import argparse
import logging
import pathlib
import subprocess
import sys
import tempfile
import traceback

import tomli


def setup_venv(workspace_path: pathlib.Path):
    """Create Python venv in which the user code will be installed."""
    logging.info("Setup Python virtual environment")

    venv_path = workspace_path / "venv"
    setup_script = f"""
        python3 -m venv --system-site-packages {venv_path};
        . {venv_path}/bin/activate;
        pip install -U pip wheel;
    """
    subprocess.run(["bash", "-c", setup_script], check=True)


def install_user_python_package(
    workspace_path: pathlib.Path,
    package_path: pathlib.Path,
):
    """Install the user's Python package into the virtual environment."""
    logging.info("Install user code in virtual environment")

    venv_path = workspace_path / "venv"
    setup_script = f"""
        . {venv_path}/bin/activate;
        pip install {package_path};
    """
    subprocess.run(["bash", "-c", setup_script], check=True)


def load_config(package_path: pathlib.Path):
    """Load and check the user's trifinger.toml."""
    logging.info("Load user configuration")
    with open(package_path / "trifinger.toml", "rb") as f:
        config = tomli.load(f)

    try:
        config = config["rrc2022"]
    except KeyError:
        raise RuntimeError("trifinger.toml: Missing section 'rrc2022'")

    try:
        task = config["task"]
    except KeyError:
        raise RuntimeError("trifinger.toml: Missing value rrc2022.task")
    assert task in ["push", "lift"], "trifinger.toml: Invalid task '{}'".format(task)

    try:
        dataset_type = config["dataset_type"]
    except KeyError:
        raise RuntimeError("trifinger.toml: Missing value rrc2022.dataset_type")
    assert dataset_type in [
        "expert",
        "mixed",
    ], "trifinger.toml: Invalid dataset_type '{}'".format(dataset_type)

    policy_key = "{}_{}_policy".format(task, dataset_type)
    assert policy_key in config, f"trifinger.toml: Missing value rrc2022.{policy_key}"

    return config


def validate_policy(workspace_path: pathlib.Path, task: str, policy: str):
    """Run _validate_policy.py which tries to import and validate the policy class."""
    logging.info("Validate policy")
    here = pathlib.Path(__file__).parent
    venv_path = workspace_path / "venv"

    setup_script = f"""
        . {venv_path}/bin/activate;
        python3 {here}/_validate_policy.py {task} {policy};
    """
    try:
        subprocess.run(["bash", "-c", setup_script], check=True)
    except subprocess.CalledProcessError:
        raise RuntimeError("Invalid policy. See output above for more information.")


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "package_dir",
        type=pathlib.Path,
        nargs="?",
        default=".",
        help="Path to the Python package.  Defaults to the current directory.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print traceback in case of error."
    )
    args = parser.parse_args()

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = pathlib.Path(tmpdir)
            logging.info("Use temporary directory %s", tmpdir)

            config = load_config(args.package_dir)

            # create venv in temporary directory
            setup_venv(tmpdir_path)

            # install the package into the venv
            install_user_python_package(tmpdir_path, args.package_dir)

            # try to import and check the policy class
            policy_key = "{task}_{dataset_type}_policy".format(**config)
            validate_policy(tmpdir_path, config["task"], config[policy_key])
    except Exception as e:
        print("\n")
        logging.error("ERROR: %s", e)
        if args.verbose:
            traceback.print_exc()
    else:
        print("\n")
        logging.info("All checks were successful :)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
