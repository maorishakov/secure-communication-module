import struct
from .message import Message, MessageType

MAGIC = b"SC"
VERSION = 1

# ! = network(big-endian)
# 2s = 2 bytes string (MAGIC)
# B  = uint8 (VERSION)
# B  = uint8 (msg_type)
# I  = uint32 (payload length)
# H  = uint16 (seq)
_HEADER_FMT = "!2sBBIH"
_HEADER_SIZE = struct.calcsize(_HEADER_FMT)


class ProtocolError(ValueError):
    pass

# Message → bytes

def encode_message(msg: Message) -> bytes:
    if not (0 <= msg.seq <= 0xFFFF):
        raise ProtocolError("seq must be in range 0..65535")

    if not isinstance(msg.payload, (bytes, bytearray)):
        raise ProtocolError("payload must be bytes")

    payload = bytes(msg.payload)
    header = struct.pack(
        _HEADER_FMT,
        MAGIC,
        VERSION,
        int(msg.msg_type),
        len(payload),
        msg.seq,
    )
    return header + payload


#bytes → Message

def decode_message(frame: bytes) -> Message:
    if len(frame) < _HEADER_SIZE:
        raise ProtocolError("frame too short")

    magic, version, msg_type, length, seq = struct.unpack(
        _HEADER_FMT, frame[:_HEADER_SIZE]
    )

    if magic != MAGIC:
        raise ProtocolError("bad magic")

    if version !=   VERSION:
        raise ProtocolError("unsupported version")

    if len(frame) != _HEADER_SIZE + length:
        raise ProtocolError("length mismatch")

    payload = frame[_HEADER_SIZE:]
    try:
        mtype = MessageType(msg_type)
    except ValueError as e:
        raise ProtocolError(f"unknown msg_type: {msg_type}") from e

    return Message(msg_type=mtype, seq=seq, payload=payload)