from .framing import decode_message, decode_header, HEADER_SIZE, ProtocolError
from .message import Message


"""
Take the bytes that come from recv() (in unexpected chunks), and extract a complete message list from them
"""

class StreamParser:

    def __init__(self):
        self._buf = bytearray()

    # return a list of complete messages
    def feed(self, data: bytes) -> list[Message]:

        messages = []

        if not data:
            return messages

        self._buf.extend(data)

        while True:
            # not enough bytes for header
            if len(self._buf) < HEADER_SIZE:
                break

            header_bytes = bytes(self._buf[:HEADER_SIZE])
            msg_type, payload_length, seq = decode_header(header_bytes)

            frame_size = HEADER_SIZE + payload_length

            # not enough bytes for frame
            if len(self._buf) < frame_size:
                break

            frame = bytes(self._buf[:frame_size])
            msg = decode_message(frame)
            messages.append(msg)

            del self._buf[:frame_size]

        return messages

    def reset(self):
        self._buf.clear()
