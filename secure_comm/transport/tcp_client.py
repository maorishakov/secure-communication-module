import socket
from typing import Optional

from secure_comm.protocol.message import Message, MessageType
from secure_comm.protocol.framing import encode_message


class TCPClient:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._sock: Optional[socket.socket] = None

    def connect(self) -> None:
        if self._sock is not None:
            raise RuntimeError("TCPClient is already connected")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        self._sock = sock
        print(f"Connected to server at {self.host}:{self.port}")

    def send(self, msg: Message) -> None:
        if self._sock is None:
            raise RuntimeError("TCPClient is not connected. Call connect() first.")

        frame = encode_message(msg)
        self._sock.sendall(frame)
        print(f"Sent: type={msg.msg_type.name} seq={msg.seq} payload_len={len(msg.payload)}")

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            finally:
                self._sock = None
                print("Connection closed")

    # Message → framing.encode_message → sendall
    def send_message(self, msg: Message) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
            frame = encode_message(msg)
            client_socket.sendall(frame)  # Data must be encoded to bytes
            print(f"Sent: {msg}")
