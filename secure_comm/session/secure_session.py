import time
from secure_comm.protocol.message import Message, MessageType
from secure_comm.transport.tcp_client import TCPClient


class SecureSession:

    def __init__(self, transport: TCPClient):
        self._transport = transport
        self._handshake_complete = False
        self._seq_counter = 0

    def _next_seq(self) -> int:
        self._seq_counter += 1
        return self._seq_counter

    def handshake_client(self, timeout_s: float = 3.0) -> None:
        msg = Message(msg_type=MessageType.HANDSHAKE_HELLO, seq=self._next_seq(), payload=b"")
        self._transport.send(msg)
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:

            remaining = deadline - time.monotonic()

            reply = self._transport.receive(min(0.5, remaining))
            if reply is None:
                continue

            if reply.msg_type == MessageType.HANDSHAKE_REPLY:
                self._handshake_complete = True
                return

        raise TimeoutError("Handshake timed out")
