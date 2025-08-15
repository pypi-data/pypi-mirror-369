# (C) 2024 Raymond Ndibe <rndibe@wikimedia.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

import pytest

from tjf_cli.cli import _job_to_arg_parser_args


@pytest.mark.parametrize(
    "json, expected_args, warning",
    [  # all keys
        [
            {
                "name": "test-job",
                "command": "./myothercommand.py -v",
                "image": "bullseye",
                "no-filelog": True,
                "filelog": True,
                "filelog-stdout": "/abc",
                "filelog-stderr": "/xyz",
                "retry": 0,
                "mem": "500Mi",
                "cpu": "500m",
                "emails": "none",
                "mount": "none",
                "schedule": "0 0 * * *",
                "continuous": True,
                "wait": True,
                "health-check-script": "./health-check.sh",
                "health-check-http": "/healthz",
                "port": 8080,
            },
            [
                "test-job",
                "--command",
                "./myothercommand.py -v",
                "--image",
                "bullseye",
                "--no-filelog",
                "--filelog",
                "--filelog-stdout",
                "/abc",
                "--filelog-stderr",
                "/xyz",
                "--retry",
                "0",
                "--mem",
                "500Mi",
                "--cpu",
                "500m",
                "--emails",
                "none",
                "--mount",
                "none",
                "--schedule",
                "0 0 * * *",
                "--continuous",
                "--wait",
                "--health-check-script",
                "./health-check.sh",
                "--health-check-http",
                "/healthz",
                "--port",
                "8080",
            ],
            "",
        ],
        [  # name not present. omit name alone, deferring validation error to arg_parser
            {"command": "./myothercommand.py -v", "image": "bullseye"},
            [
                "--command",
                "./myothercommand.py -v",
                "--image",
                "bullseye",
            ],
            "",
        ],
        [  # keys that expect string/integer should always convert any value to string."
            # Let arg_parser decide if the values are valid
            {
                "command": True,
                "image": False,
                "filelog-stdout": None,
                "filelog-stderr": 2,
                "mem": {},
                "cpu": [],
                "retry": 0,
                "port": {},
            },
            [
                "--command",
                "True",
                "--image",
                "False",
                "--filelog-stdout",
                "None",
                "--filelog-stderr",
                "2",
                "--mem",
                "{}",
                "--cpu",
                "[]",
                "--retry",
                "0",
                "--port",
                "{}",
            ],
            "",
        ],
        # wait is skipped if set to False and added for any other value.
        # arg_parser will decide if the value is valid
        [{"wait": False}, [], "omitting"],
        [{"wait": "random-text"}, ["--wait", "random-text"], ""],
        [{"wait": 40}, ["--wait", "40"], ""],
        # filelog is skipped if set to False, added if set to True or "yes", otherwise raises an exception
        [{"filelog": False}, [], "omitting"],
        [{"filelog": "yes"}, ["--filelog"], "deprecated in future releases"],
        [{"filelog": "random-text"}, [], "omitting"],
        [{"filelog": 0}, [], "omitting"],
        # no-filelog is skipped if set to False, added if set to True or "true", otherwise raises an exception
        [{"no-filelog": False}, [], "omitting"],
        [{"no-filelog": "random-text"}, [], "omitting"],
        [{"no-filelog": 0, "continuous": 0}, [], "omitting"],
        [{"no-filelog": "true"}, ["--no-filelog"], "deprecated in future releases"],
        # continuous is skipped if set to False and added if set to True, otherwise raise exception
        [{"continuous": False}, [], "omitting"],
        [{"continuous": "random-text"}, [], "omitting"],
        [{"continuous": 0}, [], "omitting"],
    ],
)
def test_job_to_arg_parser_args(
    caplog,
    json: dict,
    expected_args: list[str],
    warning: str,
):
    """
    Test that the function correctly converts a dictionary
    to a list of valid arg_parser arguments.

    Here we don't test that the arguments are valid job arguments,
    that is the work of the arg_parser.
    """

    assert _job_to_arg_parser_args(job=json) == expected_args
    assert warning in caplog.text
