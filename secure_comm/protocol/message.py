from enum import IntEnum
from dataclasses import dataclass

class MessageType(IntEnum):

    HANDSHAKE_HELLO = 1
    HANDSHAKE_REPLY = 2
    DATA = 100
    PING = 200
    PONG = 201
    ERROR = 250


@dataclass(frozen=True, slots=True)
class Message:
    msg_type: MessageType
    seq: int
    payload: bytes = b""
