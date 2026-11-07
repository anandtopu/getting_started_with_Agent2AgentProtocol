"""Run the trusted grader against the selected attempt."""

from gym.engine import check_from_test


def test_acceptance():
    check_from_test(__file__)
