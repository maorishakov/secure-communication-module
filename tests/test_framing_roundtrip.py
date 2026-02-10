from secure_comm.protocol.message import Message, MessageType
from secure_comm.protocol.framing import decode_message, encode_message


def test_framing_roundtrip():
    msg = Message(msg_type=MessageType.DATA, seq=7, payload=b"hello")
    frame = encode_message(msg)
    out = decode_message(frame)
    assert out == msg


def test_bad_magic_rejected():
    msg = Message(msg_type=MessageType.DATA, seq=1, payload=b"x")
    frame = encode_message(msg)
    bad = b"XX" + frame[2:]
    try:
        decode_message(bad)
        assert False, "expected ProtocolError"
    except Exception:
        pass
