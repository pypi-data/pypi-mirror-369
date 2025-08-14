import io
import typing
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import ANY, Mock, patch

from runem.config_metadata import ConfigMetadata
from runem.job import Job
from runem.job_runner_simple_command import job_runner_simple_command
from runem.types.runem_config import JobConfig
from tests.utils.gen_dummy_config_metadata import gen_dummy_config_metadata


@patch(
    "runem.job_runner_simple_command.run_command",
    # return_value=None,
)
def test_job_runner_simple_command(mock_run_command: Mock) -> None:
    """Tests the basics of job_runner_simple_command."""
    job_config: JobConfig = {
        "command": "echo 'testing job_runner_simple_command'",
    }
    config_metadata: ConfigMetadata = gen_dummy_config_metadata()
    with io.StringIO() as buf, redirect_stdout(buf):
        ret: None = job_runner_simple_command(  # type: ignore[func-returns-value]
            config_metadata=config_metadata,
            options=config_metadata.options,  # type: ignore
            file_list=[],
            procs=config_metadata.args.procs,
            root_path=Path("."),
            verbose=True,  # config_metadata.args.verbose,
            # unpack useful data points from the job_config
            label=Job.get_job_name(job_config),
            job=job_config,
        )
        run_command_stdout = buf.getvalue()

    assert ret is None
    assert run_command_stdout.split("\n") == [""]
    mock_run_command.assert_called_once_with(
        cmd=["echo", '"testing job_runner_simple_command"'],
        config_metadata=ANY,
        file_list=[],
        job={"command": "echo 'testing job_runner_simple_command'"},
        label="echo 'testing job_runner_simple_command'",
        options=ANY,
        procs=1,
        root_path=Path("."),
        verbose=True,
    )


@patch(
    "runem.job_runner_simple_command.run_command",
    # return_value=None,
)
def test_job_runner_simple_command_with_file_list(mock_run_command: Mock) -> None:
    """Tests the basics of job_runner_simple_command."""
    test_cmd_string: str = (
        'echo "some option before files" {file_list} "some option after files"'
    )
    job_config: JobConfig = {
        "command": test_cmd_string,
    }
    config_metadata: ConfigMetadata = gen_dummy_config_metadata()
    file_list: typing.List[typing.Union[str, Path]] = [
        Path("file1"),
        "file2",
        "file with spaces",
    ]
    with io.StringIO() as buf, redirect_stdout(buf):
        ret: None = job_runner_simple_command(  # type: ignore[func-returns-value]
            file_list=file_list,  # type: ignore[arg-type] # intentional type mismatch
            job=job_config,
            label=Job.get_job_name(job_config),
            config_metadata=config_metadata,
            options=config_metadata.options,  # type: ignore
            procs=config_metadata.args.procs,
            root_path=Path("."),
            verbose=True,  # config_metadata.args.verbose,
        )
        run_command_stdout = buf.getvalue()

    assert ret is None
    assert run_command_stdout.split("\n") == [""]
    mock_run_command.assert_called_once_with(
        cmd=[
            "echo",
            '"some option before files"',
            "file1",
            "file2",
            '"file with spaces"',
            '"some option after files"',
        ],
        config_metadata=ANY,
        file_list=file_list,
        job=job_config,
        label=test_cmd_string,
        options=ANY,
        procs=1,
        root_path=Path("."),
        verbose=True,
    )


@patch(
    "runem.job_runner_simple_command.run_command",
    # return_value=None,
)
def test_job_runner_simple_command_with_option(mock_run_command: Mock) -> None:
    """Tests that option-passing to jobs, pass --option_on but not --option_off."""
    test_cmd_string: str = (
        'echo "some option before switch" {option_on} '
        '{option_off} "some option after switch"'
    )
    job_config: JobConfig = {
        "command": test_cmd_string,
    }
    config_metadata: ConfigMetadata = gen_dummy_config_metadata()
    file_list: typing.List[typing.Union[str, Path]] = [
        Path("file1"),
        "file2",
        "file with spaces",
    ]
    with io.StringIO() as buf, redirect_stdout(buf):
        ret: None = job_runner_simple_command(  # type: ignore[func-returns-value]
            file_list=file_list,  # type: ignore[arg-type] # intentional type mismatch
            job=job_config,
            label=Job.get_job_name(job_config),
            config_metadata=config_metadata,
            options=config_metadata.options,  # type: ignore
            procs=config_metadata.args.procs,
            root_path=Path("."),
            verbose=True,  # config_metadata.args.verbose,
        )
        run_command_stdout = buf.getvalue()

    assert ret is None
    assert run_command_stdout.split("\n") == [""]
    mock_run_command.assert_called_once_with(
        cmd=[
            "echo",
            '"some option before switch"',
            "--option_on",
            # Not this -> "--option_off",
            '"some option after switch"',
        ],
        config_metadata=ANY,
        file_list=file_list,
        job=job_config,
        label=test_cmd_string,
        options={"option_on": True, "option_off": False},
        procs=1,
        root_path=Path("."),
        verbose=True,
    )
