RRC 2022 Example Package
========================

This is the official example package for the [Real Robot Challenge
2022](https://real-robot-challenge.com).  You can use it as base for your own
package when participating in the challenge.


Example Policies
----------------

The package contains two example policies for the pre-stage to show how your
package/code should be set up for running the evaluation.  You use them to test the
evaluation.

For the push task:

    $ python3 -m rrc_2022_datasets.evaluate_pre_stage push rrc2022.example.TorchPushPolicy --n-episodes=3 -v

For the lift task:

    $ python3 -m rrc_2022_datasets.evaluate_pre_stage lift rrc2022.example.TorchLiftPolicy --n-episodes=3 -v

The policy classes are implemented in `rrc2022/example.py`.  The corresponding torch
models are in `rrc2022/policies` and are installed as package_data so they can be loaded
at runtime (see `setup.cfg`).


Documentation
-------------

For more information, please see the [challenge
website](https://real-robot-challenge.com) and the [software
documentation](https://webdav.tuebingen.mpg.de/real-robot-challenge/2022/docs/).
