import pytest

from secure_comm.protocol.message import Message, MessageType
from secure_comm.protocol.framing import encode_message
from secure_comm.protocol.stream_parser import StreamParser


def make_message(seq: int, payload: bytes) -> Message:
    return Message(msg_type=MessageType.DATA, seq=seq, payload=payload)


# ------------------------------------------------------------
# 1. payload split across two feeds
# ------------------------------------------------------------

def test_stream_parser_payload_split():
    parser = StreamParser()

    msg = make_message(1, b"hello world")
    frame = encode_message(msg)

    # split somewhere inside payload
    split_point = 15
    part1 = frame[:split_point]
    part2 = frame[split_point:]

    out1 = parser.feed(part1)
    assert out1 == []  # not enough data yet

    out2 = parser.feed(part2)
    assert len(out2) == 1
    assert out2[0] == msg


# ------------------------------------------------------------
# 2. header split across two feeds
# ------------------------------------------------------------

def test_stream_parser_header_split():
    parser = StreamParser()

    msg = make_message(2, b"abcdef")
    frame = encode_message(msg)

    # split inside header
    part1 = frame[:5]
    part2 = frame[5:]

    out1 = parser.feed(part1)
    assert out1 == []  # header incomplete

    out2 = parser.feed(part2)
    assert len(out2) == 1
    assert out2[0] == msg


# ------------------------------------------------------------
# 3. two frames in single chunk
# ------------------------------------------------------------

def test_stream_parser_two_frames_together():
    parser = StreamParser()

    msg1 = make_message(3, b"first")
    msg2 = make_message(4, b"second")

    frame1 = encode_message(msg1)
    frame2 = encode_message(msg2)

    combined = frame1 + frame2

    out = parser.feed(combined)

    assert len(out) == 2
    assert out[0] == msg1
    assert out[1] == msg2


# ------------------------------------------------------------
# 4. multiple frames across multiple feeds
# ------------------------------------------------------------

def test_stream_parser_multiple_chunks_mixed():
    parser = StreamParser()

    msg1 = make_message(5, b"one")
    msg2 = make_message(6, b"two")
    msg3 = make_message(7, b"three")

    combined = (
        encode_message(msg1)
        + encode_message(msg2)
        + encode_message(msg3)
    )

    # break into weird TCP-like chunks
    chunks = [
        combined[:7],
        combined[7:20],
        combined[20:35],
        combined[35:],
    ]

    outputs = []
    for chunk in chunks:
        outputs.extend(parser.feed(chunk))

    assert outputs == [msg1, msg2, msg3]


# ------------------------------------------------------------
# 5. reset clears buffer
# ------------------------------------------------------------

def test_stream_parser_reset_clears_buffer():
    parser = StreamParser()

    msg = make_message(8, b"reset-test")
    frame = encode_message(msg)

    part1 = frame[:10]  # header only
    parser.feed(part1)

    # buffer should contain partial frame
    parser.reset()

    # now feeding remainder should NOT reconstruct message
    part2 = frame[10:]
    with pytest.raises(Exception):
        parser.feed(part2)



