import socket
import threading
import queue

from secure_comm.protocol.stream_parser import StreamParser
from secure_comm.protocol.framing import encode_message
from secure_comm.protocol.message import Message


class TCPClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

        self._sock: socket.socket | None = None
        self._parser = StreamParser()
        self._inbox: "queue.Queue[Message]" = queue.Queue()
        self._rx_thread: threading.Thread | None = None
        self._connected = False

    def _rx_loop(self):
        while self._connected:
            data = self._sock.recv(4096)
            if not data:
                break

            messages = self._parser.feed(data)
            for msg in messages:
                self._inbox.put(msg)

        self._connected = False

    def connect(self):
        if self._connected:
            return

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self.host, self.port))
        self._connected = True

        self._rx_thread = threading.Thread(
            target=self._rx_loop,
            daemon=True
        )
        self._rx_thread.start()

        print(f"Connected to server at {self.host}:{self.port}")

    def send(self, msg: Message):
        if not self._connected:
            raise RuntimeError("Client not connected")

        frame = encode_message(msg)
        self._sock.sendall(frame)
        print(f"Sent: type={msg.msg_type.name} seq={msg.seq} payload_len={len(msg.payload)}")
        print(f"Payload={msg.payload}")

    def receive(self, timeout: float | None = None) -> Message | None:
        try:
            return self._inbox.get(timeout=timeout)
        except queue.Empty:
            return None

    def close(self):
        if not self._connected:
            return

        self._connected = False
        self._sock.close()

        print("Client disconnected")
