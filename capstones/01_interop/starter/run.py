"""Runnable starting point: inspect the event before designing the network."""

from common.data import load
from common.pretty import show


def main() -> None:
    # YOUR CODE HERE: implement the project contract described in README.md.
    show(load("events/event-01.json"))


if __name__ == "__main__":
    main()
