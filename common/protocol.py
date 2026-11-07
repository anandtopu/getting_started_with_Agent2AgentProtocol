"""ProtoJSON boundaries: Python field names and JSON field names are not interchangeable."""

from uuid import uuid4

from a2a.types import Message, Part, Role, SendMessageRequest
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.struct_pb2 import Value


def data_part(value: object) -> Part:
    return Part(data=ParseDict(value, Value()), media_type="application/json")


def request(brief: dict, *, task_id: str = "", context_id: str = "") -> SendMessageRequest:
    return SendMessageRequest(
        message=Message(
            message_id=str(uuid4()),
            role=Role.ROLE_USER,
            parts=[data_part(brief)],
            task_id=task_id,
            context_id=context_id,
        )
    )


def as_dict(message) -> dict:
    return MessageToDict(message)


def brief_from(message: Message) -> dict:
    for part in message.parts:
        if part.HasField("data"):
            value = MessageToDict(part.data)
            if not isinstance(value, dict):
                raise ValueError("An event brief must be a JSON object.")
            return value
    return {"guests": 40, "date": "2027-06-01"}
