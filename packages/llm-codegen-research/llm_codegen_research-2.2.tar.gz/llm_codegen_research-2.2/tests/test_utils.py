"""Tests for various utility functions."""

import time

import pytest

from llm_cgr import TimeoutException, experiment, timeout


def test_experiment_decorator_success(capfd):
    """
    Test the experiment decorator when the experiment completes successfully.
    """

    @experiment
    def sample_experiment():
        return "Experiment completed"

    result = sample_experiment()
    assert result == "Experiment completed"

    # capture the output
    captured = capfd.readouterr()
    output = captured.out.strip().split("\n")

    # check the start and end messages
    assert output[0].startswith("===== STARTING EXPERIMENT")
    assert output[-1].startswith("===== FINISHED EXPERIMENT")
    assert len(output) == 2  # Only start and end messages should be printed


def test_experiment_decorator_exception(capfd):
    """
    Test the experiment decorator when an exception is raised.
    """

    @experiment
    def sample_experiment():
        raise ValueError("Test error")

    result = sample_experiment()
    assert result is None

    # capture the output
    captured = capfd.readouterr()
    output = captured.out.strip().split("\n")

    # check the start and end messages
    assert output[0].startswith("===== STARTING EXPERIMENT")
    assert output[-1].startswith("===== EXPERIMENT FAILED")
    assert (
        len(output) > 2
    )  # exacted length depends on the host, at least start / error / end messages


def test_timeout_context():
    """
    Test the timeout context manager.
    """
    with timeout(1):
        time.sleep(0.5)  # should complete fine

    with pytest.raises(TimeoutException, match="Execution exceeded 1s"):
        with timeout(1):
            time.sleep(2)  # should raise TimeoutException
