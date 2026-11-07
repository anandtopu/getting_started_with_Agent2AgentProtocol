"""Readable protocol objects without changing their wire representation."""

from google.protobuf.message import Message
from rich import print_json

from common.protocol import as_dict


def show(value: object) -> None:
    print_json(data=as_dict(value) if isinstance(value, Message) else value)
