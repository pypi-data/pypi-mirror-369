from typing import Any

import pytest

from tjf_cli.cli import is_default_filelog_file, job_prepare_for_dump


@pytest.fixture
def mock_tool_account(mocker):
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.read_text", return_value="someproject")
    mocker.patch("getpass.getuser", return_value="someproject.tf-test")


@pytest.mark.parametrize(
    ["result", "filelog", "jobname", "suffix"],
    [
        [True, "/data/project/tf-test/job.out", "job", "out"],
        [True, "/data/project/tf-test/job.err", "job", "err"],
        [True, "$TOOL_DATA_DIR/job.out", "job", "out"],
        [True, "$TOOL_DATA_DIR/job.err", "job", "err"],
        [False, "/data/project/tf-test/something", "job", "out"],
        [False, "/data/project/tf-test/something", "job", "err"],
        [False, "$TOOL_DATA_DIR/something", "job", "out"],
        [False, "$TOOL_DATA_DIR/something", "job", "err"],
        [False, "something", "job", "out"],
        [False, "something", "job", "err"],
        [True, None, "job", "out"],
        [True, "", "job", "err"],
    ],
)
def test_is_default_filelog_file(
    mock_tool_account: None, result: bool, filelog: str, jobname: str, suffix: str
):
    assert result == is_default_filelog_file(
        filelog, jobname, suffix, toolname="tf-test"
    )


DumpTestCase_1_emails = {
    "api_job": {
        "name": "emails-test",
        "cmd": "./mycommand.sh --argument1",
        "imagename": "bullseye",
        "image_state": "stable",
        "filelog": "True",
        "filelog_stdout": "/data/project/tf-test/emails-test.out",
        "filelog_stderr": "/data/project/tf-test/emails-test.err",
        "status_short": "Running for 1m24s",
        "status_long": "Last run at 2024-03-15T12:47:37Z. Pod in 'Failed' phase. [..]",
        "retry": 0,
        "mount": "all",
        "emails": "all",
        "replicas": 1,
        "health_check": None,
        "port": None,
    },
    "dump_job": {
        "name": "emails-test",
        "command": "./mycommand.sh --argument1",
        "image": "bullseye",
        "emails": "all",
    },
}

DumpTestCase_2_retry = {
    "api_job": {
        "name": "normal-job-with-custom-retry-policy",
        "cmd": "./mycommand.sh --argument1",
        "imagename": "bullseye",
        "image_state": "stable",
        "filelog": "True",
        "filelog_stdout": "/data/project/tf-test/normal-job-with-custom-retry-policy.out",
        "filelog_stderr": "/data/project/tf-test/normal-job-with-custom-retry-policy.err",
        "status_short": "Running for 1m24s",
        "status_long": "Last run at 2024-03-15T12:47:37Z. Pod in 'Failed' phase. [..]",
        "emails": "none",
        "mount": "all",
        "retry": 2,
        "replicas": 1,
        "health_check": None,
        "port": None,
    },
    "dump_job": {
        "name": "normal-job-with-custom-retry-policy",
        "command": "./mycommand.sh --argument1",
        "image": "bullseye",
        "retry": 2,
    },
}

DumpTestCase_3_mount = {
    "api_job": {
        "name": "mount-test",
        "cmd": "./mycommand.sh --argument1",
        "imagename": "tool-tf-test/tool-tf-test:latest",
        "image_state": "stable",
        "filelog": False,
        "filelog_stdout": None,
        "filelog_stderr": None,
        "status_short": "Running for 1m24s",
        "status_long": "Last run at 2024-03-15T12:47:37Z. Pod in 'Failed' phase. [..]",
        "retry": 0,
        "mount": "all",
        "emails": "none",
        "replicas": 1,
        "health_check": None,
        "port": None,
    },
    "dump_job": {
        "name": "mount-test",
        "command": "./mycommand.sh --argument1",
        "image": "tool-tf-test/tool-tf-test:latest",
        "mount": "all",
    },
}

DumpTestCase_4_mount = {
    "api_job": {
        "name": "mount-test",
        "cmd": "./mycommand.sh --argument1",
        "imagename": "tool-tf-test/tool-tf-test:latest",
        "image_state": "stable",
        "filelog": False,
        "filelog_stdout": None,
        "filelog_stderr": None,
        "status_short": "Running for 1m24s",
        "status_long": "Last run at 2024-03-15T12:47:37Z. Pod in 'Failed' phase. [..]",
        "retry": 0,
        "mount": "none",
        "emails": "none",
        "replicas": 1,
        "health_check": None,
        "port": None,
    },
    "dump_job": {
        "name": "mount-test",
        "command": "./mycommand.sh --argument1",
        "image": "tool-tf-test/tool-tf-test:latest",
    },
}

DumpTestCase_5_filelog_stdout = {
    "api_job": {
        "name": "filelog-test",
        "cmd": "./mycommand.sh --argument1",
        "imagename": "tool-tf-test/tool-tf-test:latest",
        "image_state": "stable",
        "filelog": True,
        "filelog_stdout": "/something",
        "filelog_stderr": None,
        "status_short": "Running for 1m24s",
        "status_long": "Last run at 2024-03-15T12:47:37Z. Pod in 'Failed' phase. [..]",
        "retry": 0,
        "mount": "none",
        "emails": "none",
        "replicas": 1,
        "health_check": None,
        "port": None,
    },
    "dump_job": {
        "name": "filelog-test",
        "command": "./mycommand.sh --argument1",
        "image": "tool-tf-test/tool-tf-test:latest",
        "filelog": "yes",
        "filelog-stdout": "/something",
    },
}

DumpTestCase_5_filelog_stderr = {
    "api_job": {
        "name": "filelog-test",
        "cmd": "./mycommand.sh --argument1",
        "imagename": "tool-tf-test/tool-tf-test:latest",
        "image_state": "stable",
        "filelog": True,
        "filelog_stdout": None,
        "filelog_stderr": "/something",
        "status_short": "Running for 1m24s",
        "status_long": "Last run at 2024-03-15T12:47:37Z. Pod in 'Failed' phase. [..]",
        "retry": 0,
        "mount": "none",
        "emails": "none",
        "replicas": 1,
        "health_check": None,
        "port": None,
    },
    "dump_job": {
        "name": "filelog-test",
        "command": "./mycommand.sh --argument1",
        "image": "tool-tf-test/tool-tf-test:latest",
        "filelog": "yes",
        "filelog-stderr": "/something",
    },
}

DumpTestCase_6_filelog_buildservice = {
    "api_job": {
        "name": "filelog-test",
        "cmd": "./mycommand.sh --argument1",
        "imagename": "tool-tf-test/tool-tf-test:latest",
        "image_state": "stable",
        "filelog": False,
        "filelog_stdout": None,
        "filelog_stderr": None,
        "status_short": "Running for 1m24s",
        "status_long": "Last run at 2024-03-15T12:47:37Z. Pod in 'Failed' phase. [..]",
        "retry": 0,
        "mount": "none",
        "emails": "none",
        "replicas": 1,
        "health_check": None,
        "port": None,
    },
    "dump_job": {
        "name": "filelog-test",
        "command": "./mycommand.sh --argument1",
        "image": "tool-tf-test/tool-tf-test:latest",
    },
}

DumpTestCase_7_filelog_buildservice = {
    "api_job": {
        "name": "filelog-test",
        "cmd": "./mycommand.sh --argument1",
        "imagename": "tool-tf-test/tool-tf-test:latest",
        "image_state": "stable",
        "filelog": True,
        "filelog_stdout": None,
        "filelog_stderr": None,
        "status_short": "Running for 1m24s",
        "status_long": "Last run at 2024-03-15T12:47:37Z. Pod in 'Failed' phase. [..]",
        "retry": 0,
        "mount": "none",
        "emails": "none",
        "replicas": 1,
        "health_check": None,
        "port": None,
    },
    "dump_job": {
        "name": "filelog-test",
        "command": "./mycommand.sh --argument1",
        "image": "tool-tf-test/tool-tf-test:latest",
        "filelog": "yes",
    },
}

DumpTestCase_8_filelog_non_buildservice = {
    "api_job": {
        "name": "filelog-test",
        "cmd": "./mycommand.sh --argument1",
        "imagename": "bookworm",
        "image_state": "stable",
        "filelog": False,
        "filelog_stdout": None,
        "filelog_stderr": None,
        "status_short": "Running for 1m24s",
        "status_long": "Last run at 2024-03-15T12:47:37Z. Pod in 'Failed' phase. [..]",
        "retry": 0,
        "mount": "all",
        "emails": "none",
        "replicas": 1,
        "health_check": None,
        "port": None,
    },
    "dump_job": {
        "name": "filelog-test",
        "command": "./mycommand.sh --argument1",
        "image": "bookworm",
        "no-filelog": "true",
    },
}

DumpTestCase_9_memory = {
    "api_job": {
        "name": "mem",
        "cmd": "./mycommand.sh --argument1",
        "imagename": "bookworm",
        "image_state": "stable",
        "filelog": True,
        "filelog_stdout": "/data/project/tf-test/mem.out",
        "filelog_stderr": "/data/project/tf-test/mem.err",
        "status_short": "Running for 1m24s",
        "status_long": "Last run at 2024-03-15T12:47:37Z. Pod in 'Failed' phase. [..]",
        "retry": 0,
        "mount": "all",
        "emails": "none",
        "memory": "1G",
        "replicas": 1,
        "health_check": None,
        "port": None,
    },
    "dump_job": {
        "name": "mem",
        "command": "./mycommand.sh --argument1",
        "image": "bookworm",
        "mem": "1G",
    },
}

DumpTestCase_10_filelog_path_shorten = {
    "api_job": {
        "name": "short",
        "cmd": "./mycommand.sh --argument1",
        "imagename": "bookworm",
        "image_state": "stable",
        "filelog": True,
        "filelog_stdout": "/data/project/tf-test/dir/something.out",
        "filelog_stderr": "$TOOL_DATA_DIR/dir/something.err",
        "status_short": "Running for 1m24s",
        "status_long": "Last run at 2024-03-15T12:47:37Z. Pod in 'Failed' phase. [..]",
        "retry": 0,
        "mount": "all",
        "emails": "none",
        "replicas": 1,
        "health_check": None,
        "port": None,
    },
    "dump_job": {
        "name": "short",
        "command": "./mycommand.sh --argument1",
        "image": "bookworm",
        "filelog-stdout": "dir/something.out",
        "filelog-stderr": "dir/something.err",
    },
}

DumpTestCase_11_script_healthcheck = {
    "api_job": {
        "name": "short",
        "cmd": "./mycommand.sh --argument1",
        "imagename": "bookworm",
        "image_state": "stable",
        "filelog": None,
        "filelog_stdout": None,
        "filelog_stderr": None,
        "status_short": "Running for 1m24s",
        "status_long": "Last run at 2024-03-15T12:47:37Z. Pod in 'Failed' phase. [..]",
        "retry": 0,
        "mount": "all",
        "emails": "none",
        "replicas": 1,
        "health_check": {
            "type": "script",
            "script": "./some-healthcheck-script.sh",
        },
        "port": None,
    },
    "dump_job": {
        "name": "short",
        "command": "./mycommand.sh --argument1",
        "image": "bookworm",
        "no-filelog": "true",
        "health-check-script": "./some-healthcheck-script.sh",
    },
}

DumpTestCase_12_http_healthcheck = {
    "api_job": {
        "name": "short",
        "cmd": "./mycommand.sh --argument1",
        "imagename": "bookworm",
        "image_state": "stable",
        "filelog": None,
        "filelog_stdout": None,
        "filelog_stderr": None,
        "status_short": "Running for 1m24s",
        "status_long": "Last run at 2024-03-15T12:47:37Z. Pod in 'Failed' phase. [..]",
        "retry": 0,
        "mount": "all",
        "emails": "none",
        "replicas": 1,
        "health_check": {
            "type": "http",
            "path": "/healthz",
        },
        "port": None,
    },
    "dump_job": {
        "name": "short",
        "command": "./mycommand.sh --argument1",
        "image": "bookworm",
        "no-filelog": "true",
        "health-check-http": "/healthz",
    },
}

DumpTestCase_13_port = {
    "api_job": {
        "name": "short",
        "cmd": "./mycommand.sh --argument1",
        "imagename": "bookworm",
        "image_state": "stable",
        "filelog": None,
        "filelog_stdout": None,
        "filelog_stderr": None,
        "status_short": "Running for 1m24s",
        "status_long": "Last run at 2024-03-15T12:47:37Z. Pod in 'Failed' phase. [..]",
        "retry": 0,
        "mount": "all",
        "emails": "none",
        "replicas": 1,
        "health_check": None,
        "port": 8080,
        "port_protocol": "tcp",
    },
    "dump_job": {
        "name": "short",
        "command": "./mycommand.sh --argument1",
        "image": "bookworm",
        "no-filelog": "true",
        "port": "8080/tcp",
    },
}

DumpTestCase_14_replicas = {
    "api_job": {
        "name": "short",
        "cmd": "./mycommand.sh --argument1",
        "imagename": "bookworm",
        "image_state": "stable",
        "filelog": None,
        "filelog_stdout": None,
        "filelog_stderr": None,
        "status_short": "Running for 1m24s",
        "status_long": "Last run at 2024-03-15T12:47:37Z. Pod in 'Failed' phase. [..]",
        "retry": 0,
        "mount": "all",
        "emails": "none",
        "continuous": True,
        "replicas": 1,
        "health_check": None,
        "port": None,
    },
    "dump_job": {
        "name": "short",
        "command": "./mycommand.sh --argument1",
        "image": "bookworm",
        "no-filelog": "true",
        "continuous": True,
        "replicas": 1,
    },
}


@pytest.mark.parametrize(
    ["testcase"],
    [
        [DumpTestCase_1_emails],
        [DumpTestCase_2_retry],
        [DumpTestCase_3_mount],
        [DumpTestCase_4_mount],
        [DumpTestCase_5_filelog_stdout],
        [DumpTestCase_5_filelog_stderr],
        [DumpTestCase_6_filelog_buildservice],
        [DumpTestCase_7_filelog_buildservice],
        [DumpTestCase_8_filelog_non_buildservice],
        [DumpTestCase_9_memory],
        [DumpTestCase_10_filelog_path_shorten],
        [DumpTestCase_11_script_healthcheck],
        [DumpTestCase_12_http_healthcheck],
        [DumpTestCase_13_port],
        [DumpTestCase_14_replicas],
    ],
)
def test_job_prepare_for_dump(
    mock_tool_account: None, testcase: dict[str, Any]
) -> None:
    api_job = testcase["api_job"]
    job_prepare_for_dump(api_job, toolname="tf-test")
    assert api_job == testcase["dump_job"]
