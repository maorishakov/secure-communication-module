from enum import IntEnum
from dataclasses import dataclass

"""
The language
Defines the types of messages and their structure
"""


class MessageType(IntEnum):

    HANDSHAKE_HELLO = 1
    HANDSHAKE_REPLY = 2
    DATA = 100
    PING = 200
    PONG = 201
    ERROR = 250

# frozen=True -> The object is immutable after creation

@dataclass(frozen=True, slots=True)
class Message:
    msg_type: MessageType
    seq: int
    payload: bytes = b""
